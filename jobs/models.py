from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('company', 'Company'),
        ('user', 'User'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    
    def __str__(self):
        return f"{self.user.username} - {self.role}"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

class Job(models.Model):
    title = models.CharField(max_length=200)
    company = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'profile__role': 'company'})
    location = models.CharField(max_length=200)
    description = models.TextField()
    apply_link = models.URLField(blank=True, null=True, help_text="External application link (optional)")
    posted_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title} at {self.company.username}"
    
    class Meta:
        ordering = ['-posted_at']

class Application(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('reviewed', 'Reviewed'),
        ('shortlisted', 'Shortlisted'),
        ('rejected', 'Rejected'),
        ('hired', 'Hired'),
    ]
    
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')
    cover_letter = models.TextField()
    resume = models.FileField(upload_to='resumes/', help_text="Upload your resume (PDF, DOC, DOCX)")
    applied_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    class Meta:
        ordering = ['-applied_at']
        unique_together = ['job', 'applicant']  # Prevent duplicate applications
    
    def __str__(self):
        return f"{self.applicant.username} applied for {self.job.title}"
