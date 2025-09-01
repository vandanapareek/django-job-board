# Django Job Board - Complete Development Guide for Beginners

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Project Setup](#project-setup)
3. [Django Project Structure](#django-project-structure)
4. [Database Models](#database-models)
5. [User Authentication & Roles](#user-authentication--roles)
6. [Forms](#forms)
7. [Views (Business Logic)](#views-business-logic)
8. [URLs (Routing)](#urls-routing)
9. [Templates (Frontend)](#templates-frontend)
10. [Admin Interface](#admin-interface)
11. [Static Files & Styling](#static-files--styling)
12. [Testing & Sample Data](#testing--sample-data)
13. [Common Issues & Solutions](#common-issues--solutions)

---

## Prerequisites

### What You Need to Install First:
1. **Python** (version 3.8 or higher)
2. **pip** (Python package installer)
3. **Git** (optional, for version control)

### Check Your Installation:
```bash
python --version
pip --version
```

---

## Project Setup

### Step 1: Create Project Directory
```bash
# Navigate to your desired location
cd /Users/vandana/pyhton-project

# Create a new directory for your project
mkdir jobboard-project
cd jobboard-project
```

### Step 2: Create Virtual Environment
**What is a Virtual Environment?**
- It's like a "container" for your project
- Keeps your project's dependencies separate from other projects
- Prevents conflicts between different Python packages

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# You'll see (venv) at the beginning of your command prompt
```

### Step 3: Install Django
```bash
# Install Django
pip install django

# Create requirements.txt to track dependencies
pip freeze > requirements.txt
```

### Step 4: Create Django Project
```bash
# Create the main project
django-admin startproject jobboard .

# This creates:
# - jobboard/ (main project folder)
# - manage.py (Django management script)
# - jobboard/settings.py (project settings)
# - jobboard/urls.py (main URL configuration)
# - jobboard/wsgi.py (web server gateway)
```

### Step 5: Create Django App
```bash
# Create the jobs app
python manage.py startapp jobs

# This creates:
# - jobs/ (app folder)
# - jobs/models.py (database models)
# - jobs/views.py (business logic)
# - jobs/urls.py (app URL patterns)
# - jobs/admin.py (admin interface)
```

---

## Django Project Structure

### Understanding the Structure:
```
jobboard-project/
├── venv/                    # Virtual environment
├── jobboard/               # Main project folder
│   ├── __init__.py
│   ├── settings.py         # Project settings
│   ├── urls.py            # Main URL routing
│   ├── wsgi.py            # Web server configuration
│   └── asgi.py
├── jobs/                   # Our app folder
│   ├── __init__.py
│   ├── admin.py           # Admin interface
│   ├── apps.py
│   ├── models.py          # Database models
│   ├── views.py           # Business logic
│   ├── urls.py            # App URL patterns
│   └── migrations/        # Database changes
├── manage.py              # Django management script
└── requirements.txt       # Python dependencies
```

---

## Database Models

### What are Models?
- Models define your database structure
- They're like "blueprints" for your data
- Django automatically creates database tables from models

### Step 1: Define User Profile Model
**File: `jobs/models.py`**

```python
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    # Link to Django's built-in User model
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    # User role choices
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('company', 'Company'),
        ('user', 'User'),
    ]
    
    # User's role in the system
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    
    def __str__(self):
        return f"{self.user.username} - {self.role}"

# Automatically create Profile when User is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
```

### Step 2: Define Job Model
```python
class Job(models.Model):
    title = models.CharField(max_length=200)
    company = models.ForeignKey(User, on_delete=models.CASCADE, 
                               limit_choices_to={'profile__role': 'company'})
    location = models.CharField(max_length=100)
    description = models.TextField()
    apply_link = models.URLField(blank=True, null=True)  # Optional external link
    posted_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title} at {self.company.username}"
    
    class Meta:
        ordering = ['-posted_at']
```

### Step 3: Define Application Model
```python
class Application(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    applicant = models.ForeignKey(User, on_delete=models.CASCADE)
    cover_letter = models.TextField()
    resume = models.FileField(upload_to='resumes/')
    applied_at = models.DateTimeField(auto_now_add=True)
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('reviewed', 'Reviewed'),
        ('shortlisted', 'Shortlisted'),
        ('rejected', 'Rejected'),
        ('hired', 'Hired'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    class Meta:
        unique_together = ['job', 'applicant']  # Prevent duplicate applications
```

### Step 4: Configure Settings
**File: `jobboard/settings.py`**

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'jobs',  # Add our app here
]

# Template configuration
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # Add templates directory
        'APP_DIRS': True,
        # ... rest of settings
    },
]

# Static files configuration
STATICFILES_DIRS = [BASE_DIR / 'static']

# Media files (for uploaded files)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Authentication settings
LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/login/'
LOGOUT_REDIRECT_URL = '/'
```

### Step 5: Create Database Tables
```bash
# Create database migration files
python manage.py makemigrations

# Apply migrations to create tables
python manage.py migrate
```

---

## User Authentication & Roles

### How Django Authentication Works:
1. **User Model**: Django provides a built-in User model
2. **Profile Model**: We extend it with our Profile model for roles
3. **Signals**: Automatically create Profile when User is created

### Creating Superuser (Admin):
```bash
python manage.py createsuperuser
# Username: admin
# Email: admin@example.com
# Password: admin123
```

### Setting User Roles:
```bash
# Open Django shell
python manage.py shell

# Set admin role
from django.contrib.auth.models import User
from jobs.models import Profile

admin = User.objects.get(username='admin')
admin.profile.role = 'admin'
admin.profile.save()
```

---

## Forms

### What are Forms?
- Forms handle user input
- They validate data before saving to database
- They provide HTML form fields

### Step 1: Job Form
**File: `jobs/forms.py`**

```python
from django import forms
from .models import Job, Application

class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['title', 'location', 'description', 'apply_link']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'apply_link': forms.URLInput(attrs={'class': 'form-control'}),
        }
```

### Step 2: Application Form
```python
class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['cover_letter', 'resume']
        widgets = {
            'cover_letter': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'resume': forms.FileInput(attrs={'class': 'form-control'}),
        }
    
    def clean_resume(self):
        resume = self.cleaned_data.get('resume')
        if resume:
            # Check file size (5MB limit)
            if resume.size > 5 * 1024 * 1024:
                raise forms.ValidationError("File size must be under 5MB")
            
            # Check file extension
            allowed_extensions = ['.pdf', '.doc', '.docx']
            if not any(resume.name.lower().endswith(ext) for ext in allowed_extensions):
                raise forms.ValidationError("Only PDF, DOC, and DOCX files are allowed")
        
        return resume
```

---

## Views (Business Logic)

### What are Views?
- Views contain the business logic
- They handle HTTP requests and return responses
- They connect models (data) with templates (display)

### Step 1: Job List View
**File: `jobs/views.py`**

```python
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Job, Application
from .forms import JobForm, ApplicationForm

def job_list(request):
    """Show jobs based on user role"""
    search_query = request.GET.get('search', '')
    
    if request.user.is_authenticated:
        if request.user.profile.role == 'company':
            # Companies see only their own jobs
            jobs = Job.objects.filter(company=request.user)
            page_title = "My Job Postings"
            show_add_button = True
        elif request.user.profile.role == 'admin':
            # Admins see all jobs
            jobs = Job.objects.all()
            page_title = "All Jobs (Admin View)"
            show_add_button = False
        else:
            # Regular users see all jobs
            jobs = Job.objects.all()
            page_title = "Available Jobs"
            show_add_button = False
    else:
        # Non-authenticated users see all jobs
        jobs = Job.objects.all()
        page_title = "Available Jobs"
        show_add_button = False
    
    # Apply search filter
    if search_query:
        jobs = jobs.filter(
            Q(title__icontains=search_query) |
            Q(company__username__icontains=search_query) |
            Q(location__icontains=search_query)
        )
    
    context = {
        'jobs': jobs,
        'page_title': page_title,
        'show_add_button': show_add_button,
        'search_query': search_query,
    }
    return render(request, 'jobs/job_list.html', context)
```

### Step 2: Job Detail View
```python
def job_detail(request, job_id):
    """Show detailed information about a job"""
    job = get_object_or_404(Job, id=job_id)
    has_applied = False
    application_count = 0
    
    if request.user.is_authenticated:
        # Check if user has already applied
        has_applied = Application.objects.filter(job=job, applicant=request.user).exists()
        
        # Show application count for job owners
        if request.user == job.company or request.user.profile.role == 'admin':
            application_count = Application.objects.filter(job=job).count()
    
    context = {
        'job': job,
        'has_applied': has_applied,
        'application_count': application_count,
    }
    return render(request, 'jobs/job_detail.html', context)
```

### Step 3: Add Job View (Company Only)
```python
@login_required
def add_job(request):
    """Add a new job posting (companies only)"""
    if request.user.profile.role != 'company':
        messages.error(request, "Only companies can post jobs.")
        return redirect('jobs:job_list')
    
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.company = request.user
            job.save()
            messages.success(request, "Job posted successfully!")
            return redirect('jobs:job_detail', job_id=job.id)
    else:
        form = JobForm()
    
    return render(request, 'jobs/job_form.html', {'form': form, 'action': 'Add'})
```

### Step 4: Apply for Job View
```python
@login_required
def apply_job(request, job_id):
    """Apply for a job"""
    job = get_object_or_404(Job, id=job_id)
    
    # Check if user has already applied
    if Application.objects.filter(job=job, applicant=request.user).exists():
        messages.warning(request, "You have already applied for this job.")
        return redirect('jobs:job_detail', job_id=job.id)
    
    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.applicant = request.user
            application.save()
            messages.success(request, "Application submitted successfully!")
            return redirect('jobs:job_detail', job_id=job.id)
    else:
        form = ApplicationForm()
    
    context = {
        'form': form,
        'job': job,
    }
    return render(request, 'jobs/apply_job.html', context)
```

---

## URLs (Routing)

### What are URLs?
- URLs map web addresses to views
- They define the structure of your website
- They handle URL parameters

### Step 1: Main Project URLs
**File: `jobboard/urls.py`**

```python
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from jobs.views import custom_logout

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('jobs.urls')),  # Include app URLs at root
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', custom_logout, name='logout'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

### Step 2: App URLs
**File: `jobs/urls.py`**

```python
from django.urls import path
from . import views

app_name = 'jobs'  # URL namespace

urlpatterns = [
    path('', views.job_list, name='job_list'),
    path('<int:job_id>/', views.job_detail, name='job_detail'),
    path('<int:job_id>/apply/', views.apply_job, name='apply_job'),
    path('applications/', views.my_applications, name='my_applications'),
    path('applications/<int:application_id>/', views.application_detail, name='application_detail'),
    path('company/applications/', views.company_applications, name='company_applications'),
    path('add/', views.add_job, name='add_job'),
    path('<int:job_id>/edit/', views.edit_job, name='edit_job'),
    path('<int:job_id>/delete/', views.delete_job, name='delete_job'),
]
```

---

## Templates (Frontend)

### What are Templates?
- Templates are HTML files with Django template language
- They define how your data is displayed
- They support template inheritance

### Step 1: Create Template Directory
```bash
mkdir templates
mkdir templates/jobs
mkdir templates/registration
```

### Step 2: Base Template
**File: `templates/base.html`**

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Job Board{% endblock %}</title>
    
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Font Awesome -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
</head>
<body>
    <!-- Navigation -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="{% url 'jobs:job_list' %}">
                <i class="fas fa-briefcase"></i> Job Board
            </a>
            
            <div class="navbar-nav ms-auto">
                {% if user.is_authenticated %}
                    {% if user.profile.role == 'company' %}
                        <a class="nav-link" href="{% url 'jobs:add_job' %}">
                            <i class="fas fa-plus"></i> Add Job
                        </a>
                    {% endif %}
                    
                    {% if user.profile.role == 'admin' %}
                        <a class="nav-link" href="{% url 'admin:index' %}">
                            <i class="fas fa-cog"></i> Admin Panel
                        </a>
                    {% endif %}
                    
                    {% if user.profile.role == 'user' %}
                        <a class="nav-link" href="{% url 'jobs:my_applications' %}">
                            <i class="fas fa-file-alt"></i> My Applications
                        </a>
                    {% endif %}
                    
                    <div class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown">
                            <i class="fas fa-user"></i> {{ user.username }}
                        </a>
                        <ul class="dropdown-menu">
                            <li><a class="dropdown-item" href="{% url 'logout' %}">Logout</a></li>
                        </ul>
                    </div>
                {% else %}
                    <a class="nav-link" href="{% url 'login' %}">
                        <i class="fas fa-sign-in-alt"></i> Login
                    </a>
                {% endif %}
            </div>
        </div>
    </nav>

    <!-- Main Content -->
    <div class="container mt-4">
        {% if messages %}
            {% for message in messages %}
                <div class="alert alert-{{ message.tags }} alert-dismissible fade show">
                    {{ message }}
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                </div>
            {% endfor %}
        {% endif %}
        
        {% block content %}
        {% endblock %}
    </div>

    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
```

### Step 3: Job List Template
**File: `templates/jobs/job_list.html`**

```html
{% extends 'base.html' %}

{% block title %}{{ page_title }}{% endblock %}

{% block content %}
<div class="row">
    <div class="col-md-8">
        <h1>{{ page_title }}</h1>
    </div>
    <div class="col-md-4 text-end">
        {% if show_add_button %}
            <a href="{% url 'jobs:add_job' %}" class="btn btn-primary">
                <i class="fas fa-plus"></i> Post a Job
            </a>
        {% endif %}
    </div>
</div>

<!-- Search Form -->
<form method="get" class="mb-4">
    <div class="input-group">
        <input type="text" name="search" class="form-control" 
               placeholder="Search jobs..." value="{{ search_query }}">
        <button type="submit" class="btn btn-outline-secondary">
            <i class="fas fa-search"></i> Search
        </button>
    </div>
</form>

<!-- Jobs List -->
<div class="row">
    {% for job in jobs %}
    <div class="col-md-6 mb-4">
        <div class="card h-100">
            <div class="card-body">
                <h5 class="card-title">{{ job.title }}</h5>
                <h6 class="card-subtitle mb-2 text-muted">
                    <i class="fas fa-building"></i> {{ job.company.username }}
                </h6>
                <p class="card-text">
                    <i class="fas fa-map-marker-alt"></i> {{ job.location }}
                </p>
                <p class="card-text">{{ job.description|truncatewords:30 }}</p>
                <a href="{% url 'jobs:job_detail' job.id %}" class="btn btn-primary">
                    View Details
                </a>
            </div>
            <div class="card-footer text-muted">
                Posted {{ job.posted_at|timesince }} ago
            </div>
        </div>
    </div>
    {% empty %}
    <div class="col-12">
        <div class="alert alert-info">
            No jobs found. {% if show_add_button %}Be the first to post a job!{% endif %}
        </div>
    </div>
    {% endfor %}
</div>
{% endblock %}
```

---

## Admin Interface

### What is Django Admin?
- Built-in admin interface for managing data
- Automatically generated from your models
- Great for content management

### Configure Admin
**File: `jobs/admin.py`**

```python
from django.contrib import admin
from .models import Profile, Job, Application

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role']
    list_filter = ['role']
    search_fields = ['user__username', 'user__email']

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ['title', 'company', 'location', 'posted_at', 'application_count']
    list_filter = ['posted_at', 'company__profile__role']
    search_fields = ['title', 'company__username', 'location']
    
    def application_count(self, obj):
        return obj.application_set.count()
    application_count.short_description = 'Applications'

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ['job', 'applicant', 'status', 'applied_at']
    list_filter = ['status', 'applied_at']
    search_fields = ['job__title', 'applicant__username']
    
    fieldsets = (
        ('Job Information', {
            'fields': ('job', 'applicant')
        }),
        ('Application Details', {
            'fields': ('cover_letter', 'resume', 'status')
        }),
        ('Timestamps', {
            'fields': ('applied_at',),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('applied_at',)
```

---

## Static Files & Styling

### What are Static Files?
- CSS, JavaScript, images
- Files that don't change based on user input
- Served directly to the browser

### Create Static Directory
```bash
mkdir static
mkdir static/css
```

### Custom CSS
**File: `static/css/style.css`**

```css
/* Custom styles for job cards */
.job-card {
    transition: transform 0.2s;
}

.job-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

/* Application status badges */
.status-pending { background-color: #ffc107; }
.status-reviewed { background-color: #17a2b8; }
.status-shortlisted { background-color: #28a745; }
.status-rejected { background-color: #dc3545; }
.status-hired { background-color: #6f42c1; }
```

---

## Testing & Sample Data

### Create Sample Data Command
**File: `jobs/management/commands/create_sample_data.py`**

```python
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from jobs.models import Job, Profile
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = 'Create sample data for the job board'

    def handle(self, *args, **options):
        # Create admin user
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@jobboard.com',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            admin_user.profile.role = 'admin'
            admin_user.profile.save()
            self.stdout.write(f'Created admin user: {admin_user.username}')

        # Create company users
        companies = [
            {'username': 'techcorp', 'email': 'hr@techcorp.com'},
            {'username': 'innovate', 'email': 'careers@innovate.com'},
        ]
        
        for company_data in companies:
            company_user, created = User.objects.get_or_create(
                username=company_data['username'],
                defaults={'email': company_data['email']}
            )
            if created:
                company_user.set_password('company123')
                company_user.save()
                company_user.profile.role = 'company'
                company_user.profile.save()
                self.stdout.write(f'Created company user: {company_user.username}')

        # Create regular users
        users = [
            {'username': 'john_doe', 'email': 'john@example.com'},
            {'username': 'jane_smith', 'email': 'jane@example.com'},
        ]
        
        for user_data in users:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={'email': user_data['email']}
            )
            if created:
                user.set_password('user123')
                user.save()
                self.stdout.write(f'Created user: {user.username}')

        # Create sample jobs
        techcorp = User.objects.get(username='techcorp')
        innovate = User.objects.get(username='innovate')
        
        jobs_data = [
            {
                'title': 'Senior Python Developer',
                'company': techcorp,
                'location': 'San Francisco, CA',
                'description': 'We are looking for an experienced Python developer...',
            },
            {
                'title': 'Product Manager',
                'company': innovate,
                'location': 'New York, NY',
                'description': 'Join our product team to build amazing products...',
            },
        ]
        
        for job_data in jobs_data:
            job, created = Job.objects.get_or_create(
                title=job_data['title'],
                company=job_data['company'],
                defaults=job_data
            )
            if created:
                self.stdout.write(f'Created job: {job.title}')

        self.stdout.write(self.style.SUCCESS('Sample data created successfully!'))
```

### Run Sample Data Command
```bash
python manage.py create_sample_data
```

---

## Common Issues & Solutions

### Issue 1: "django-admin command not found"
**Solution:**
```bash
# Make sure you're in your virtual environment
source venv/bin/activate

# Install Django if not installed
pip install django
```

### Issue 2: Login redirecting to wrong URL
**Solution:**
Add to `settings.py`:
```python
LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/login/'
LOGOUT_REDIRECT_URL = '/'
```

### Issue 3: Static files not loading
**Solution:**
1. Add to `settings.py`:
```python
STATICFILES_DIRS = [BASE_DIR / 'static']
```

2. Add to main `urls.py`:
```python
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
```

### Issue 4: Media files not uploading
**Solution:**
1. Add to `settings.py`:
```python
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

2. Add to main `urls.py`:
```python
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

### Issue 5: Database migration errors
**Solution:**
```bash
# Delete all migration files (except __init__.py)
rm jobs/migrations/0*.py

# Recreate migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate
```

---

## Running the Project

### Start Development Server
```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Run the server
python manage.py runserver

# Open browser to http://127.0.0.1:8000/
```

### Test Different User Roles
1. **Admin**: `admin` / `admin123`
2. **Company**: `techcorp` / `company123`
3. **User**: `john_doe` / `user123`

---

## Key Concepts Summary

1. **MVC Pattern**: Django follows Model-View-Controller pattern
   - **Models**: Define database structure (`models.py`)
   - **Views**: Handle business logic (`views.py`)
   - **Templates**: Display data (`templates/`)

2. **URL Routing**: Maps URLs to views (`urls.py`)

3. **Forms**: Handle user input and validation (`forms.py`)

4. **Admin Interface**: Built-in data management (`admin.py`)

5. **Static Files**: CSS, JS, images for styling

6. **Media Files**: User-uploaded content (resumes, etc.)

This guide covers the complete development process from scratch. Each section builds upon the previous one, creating a fully functional job board application with user roles, job postings, and applications.
