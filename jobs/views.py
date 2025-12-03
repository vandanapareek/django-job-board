import logging

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.contrib.auth import logout
from django.http import HttpResponseRedirect, JsonResponse
from django.views.decorators.http import require_POST
from .models import Job, Application
from .forms import JobForm, ApplicationForm
from .services import (
    build_candidate_match_payload,
    save_candidate_skills_from_text,
    extract_text_from_resume,
    save_job_skills,
)

logger = logging.getLogger(__name__)

def custom_logout(request):
    """Custom logout view to ensure proper session clearing"""
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    response = HttpResponseRedirect('/')
    # Clear any session cookies
    response.delete_cookie('sessionid')
    response.delete_cookie('csrftoken')
    return response

def job_list(request):
    """Show jobs based on user role"""
    if request.user.is_authenticated and request.user.profile.role == 'company':
        # Companies see only their own jobs
        jobs = Job.objects.filter(company=request.user)
        page_title = "My Job Postings"
        show_add_button = True
    elif request.user.is_authenticated and request.user.profile.role == 'admin':
        # Admins see all jobs
        jobs = Job.objects.all()
        page_title = "All Job Postings (Admin View)"
        show_add_button = False
    else:
        # Regular users and non-authenticated users see all jobs
        jobs = Job.objects.all()
        page_title = "Find Your Next Opportunity"
        show_add_button = False
    
    query = request.GET.get('q')
    if query:
        jobs = jobs.filter(
            Q(title__icontains=query) | Q(location__icontains=query)
        )
    
    context = {
        'jobs': jobs,
        'query': query,
        'page_title': page_title,
        'show_add_button': show_add_button,
    }
    return render(request, 'jobs/job_list.html', context)

def job_detail(request, job_id):
    """Show details of a specific job"""
    job = get_object_or_404(Job, id=job_id)
    
    # Check if user has already applied
    has_applied = False
    if request.user.is_authenticated and request.user.profile.role == 'user':
        has_applied = Application.objects.filter(job=job, applicant=request.user).exists()
    
    # Get application count for companies
    application_count = 0
    if request.user.is_authenticated and request.user.profile.role == 'company' and job.company == request.user:
        application_count = Application.objects.filter(job=job).count()
    
    can_manage_recommendations = False
    if request.user.is_authenticated:
        role = request.user.profile.role
        can_manage_recommendations = role == 'admin' or (role == 'company' and job.company == request.user)

    context = {
        'job': job,
        'has_applied': has_applied,
        'application_count': application_count,
        'can_manage_recommendations': can_manage_recommendations,
    }
    return render(request, 'jobs/job_detail.html', context)


@login_required
@require_POST
def extract_job_skills(request, job_id):
    """
    Extract skills for a job using the NLP pipeline (AJAX endpoint).
    """
    job = get_object_or_404(Job, id=job_id)
    if request.user.profile.role not in ['admin', 'company']:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    if request.user.profile.role == 'company' and job.company != request.user:
        return JsonResponse({'error': 'Permission denied'}, status=403)

    force_dictionary = request.GET.get('fallback') == '1'
    try:
        skills_payload = save_job_skills(job, force_dictionary=force_dictionary)
        return JsonResponse(
            {
                'success': True,
                'skills_count': len(skills_payload),
                'skills': skills_payload,
                'message': f"Extracted {len(skills_payload)} skills successfully.",
            }
        )
    except Exception as extraction_error:  # pragma: no cover - best effort
        logger.exception("Failed to extract skills for job %s", job.id)
        return JsonResponse(
            {'error': f'Unable to extract skills: {extraction_error}'},
            status=500,
        )

@login_required
def apply_job(request, job_id):
    """Apply for a job (only for users)"""
    job = get_object_or_404(Job, id=job_id)
    
    if request.user.profile.role != 'user':
        messages.error(request, 'Only users can apply for jobs.')
        return redirect('jobs:job_detail', job_id=job.id)
    
    # Check if already applied
    if Application.objects.filter(job=job, applicant=request.user).exists():
        messages.warning(request, 'You have already applied for this position.')
        return redirect('jobs:job_detail', job_id=job.id)
    
    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                application = form.save(commit=False)
                application.job = job
                application.applicant = request.user
                application.save()
                
                # Extract skills from cover letter and resume using NLP (best-effort)
                try:
                    # Extract from cover letter
                    save_candidate_skills_from_text(
                        user=request.user,
                        text=application.cover_letter,
                        source='cover_letter'
                    )
                    
                    # Extract from resume file if available
                    if application.resume:
                        resume_text = extract_text_from_resume(application.resume)
                        if resume_text:
                            save_candidate_skills_from_text(
                                user=request.user,
                                text=resume_text,
                                source='resume'
                            )
                except Exception as extraction_error:  # pragma: no cover - best effort
                    logger.warning(
                        "Failed to extract candidate skills for user %s: %s",
                        request.user.username,
                        extraction_error,
                    )
                messages.success(request, 'Your application has been submitted successfully!')
                return redirect('jobs:my_applications')
            except ValidationError as e:
                messages.error(request, str(e))
    else:
        form = ApplicationForm()
    
    context = {
        'form': form,
        'job': job,
    }
    return render(request, 'jobs/apply_job.html', context)

@login_required
def my_applications(request):
    """Show user's applications"""
    if request.user.profile.role != 'user':
        messages.error(request, 'Only users can view applications.')
        return redirect('jobs:job_list')
    
    applications = Application.objects.filter(applicant=request.user)
    
    context = {
        'applications': applications,
    }
    return render(request, 'jobs/my_applications.html', context)

@login_required
def application_detail(request, application_id):
    """Show details of a specific application"""
    application = get_object_or_404(Application, id=application_id)
    
    # Check permissions
    if request.user.profile.role == 'user' and application.applicant != request.user:
        messages.error(request, 'You can only view your own applications.')
        return redirect('jobs:my_applications')
    elif request.user.profile.role == 'company' and application.job.company != request.user:
        messages.error(request, 'You can only view applications for your job postings.')
        return redirect('jobs:job_list')
    
    context = {
        'application': application,
    }
    return render(request, 'jobs/application_detail.html', context)

@login_required
def add_job(request):
    """Add a new job (only for companies)"""
    if request.user.profile.role != 'company':
        messages.error(request, 'Only companies can add jobs.')
        return redirect('job_list')
    
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.company = request.user
            job.save()
            messages.success(request, 'Job posted successfully!')
            return redirect('jobs:job_detail', job_id=job.id)
    else:
        form = JobForm()
    
    context = {
        'form': form,
        'title': 'Add New Job',
    }
    return render(request, 'jobs/job_form.html', context)

@login_required
def edit_job(request, job_id):
    """Edit a job (only for the company that posted it)"""
    job = get_object_or_404(Job, id=job_id)
    
    if request.user != job.company:
        messages.error(request, 'You can only edit your own job postings.')
        return redirect('jobs:job_detail', job_id=job.id)
    
    if request.method == 'POST':
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, 'Job updated successfully!')
            return redirect('jobs:job_detail', job_id=job.id)
    else:
        form = JobForm(instance=job)
    
    context = {
        'form': form,
        'job': job,
        'title': 'Edit Job',
    }
    return render(request, 'jobs/job_form.html', context)

@login_required
def delete_job(request, job_id):
    """Delete a job (only for the company that posted it)"""
    job = get_object_or_404(Job, id=job_id)
    
    if request.user != job.company:
        messages.error(request, 'You can only delete your own job postings.')
        return redirect('jobs:job_detail', job_id=job.id)
    
    if request.method == 'POST':
        job.delete()
        messages.success(request, 'Job deleted successfully!')
        return redirect('job_list')
    
    context = {
        'job': job,
    }
    return render(request, 'jobs/job_confirm_delete.html', context)

@login_required
def company_applications(request):
    """Show all applications for company's job postings"""
    if request.user.profile.role != 'company' and request.user.profile.role != 'admin':
        messages.error(request, "Access denied. Only companies can view applications.")
        return redirect('jobs:job_list')
    
    # Get all jobs posted by the company
    company_jobs = Job.objects.filter(company=request.user)
    
    # Get all applications for these jobs
    applications = Application.objects.filter(job__in=company_jobs).select_related('job', 'applicant')
    
    context = {
        'applications': applications,
    }
    return render(request, 'jobs/company_applications.html', context)

@login_required
def update_application_status(request, application_id):
    """Update application status (AJAX endpoint)"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    
    application = get_object_or_404(Application, id=application_id)
    
    # Check if user has permission to update this application
    if request.user.profile.role == 'admin' or application.job.company == request.user:
        new_status = request.POST.get('status')
        
        if new_status in dict(Application.STATUS_CHOICES):
            old_status = application.status
            application.status = new_status
            application.save()
            
            # Get display names for status
            status_display = {
                'pending': 'Pending Review',
                'reviewed': 'Reviewed',
                'shortlisted': 'Shortlisted',
                'rejected': 'Rejected',
                'hired': 'Hired'
            }
            
            old_display = status_display.get(old_status, old_status)
            new_display = status_display.get(new_status, new_status)
            
            # Don't use Django messages for AJAX requests - only return JSON response
            return JsonResponse({
                'success': True,
                'new_status': new_status,
                'message': f"✅ Application status updated to '{new_display}' successfully!"
            })
        else:
            return JsonResponse({'error': 'Invalid status'}, status=400)
    else:
        return JsonResponse({'error': 'Permission denied'}, status=403)


@login_required
def job_recommendations(request, job_id):
    """
    Display candidate recommendations for a job based on extracted skills.
    """
    job = get_object_or_404(Job, id=job_id)

    if request.user.profile.role not in ['admin', 'company']:
        messages.error(request, "Only companies and admins can view recommendations.")
        return redirect('jobs:job_detail', job_id=job.id)
    if request.user.profile.role == 'company' and job.company != request.user:
        messages.error(request, "You can only view recommendations for your own jobs.")
        return redirect('jobs:job_detail', job_id=job.id)

    if not job.has_extracted_skills():
        messages.warning(request, "Please extract skills before viewing recommendations.")
        return redirect('jobs:job_detail', job_id=job.id)

    candidates = build_candidate_match_payload(job)

    for candidate_data in candidates:
        candidate = candidate_data['candidate']
        application = Application.objects.filter(applicant=candidate, job=job).first()
        if not application:
            application = (
                Application.objects
                .filter(applicant=candidate, job__company=job.company)
                .order_by('-applied_at')
                .first()
            )
        candidate_data['application'] = application

    context = {
        'job': job,
        'job_skills': job.get_extracted_skills(),
        'candidates': candidates,
    }
    return render(request, 'jobs/job_recommendations.html', context)
