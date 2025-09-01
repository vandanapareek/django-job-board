from django.contrib import admin
from .models import Profile, Job, Application

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'user_email']
    list_filter = ['role']
    search_fields = ['user__username', 'user__email']
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'Email'

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ['title', 'company', 'location', 'posted_at', 'application_count']
    list_filter = ['posted_at', 'company__profile__role']
    search_fields = ['title', 'company__username', 'location']
    readonly_fields = ['posted_at']
    date_hierarchy = 'posted_at'
    
    def application_count(self, obj):
        return obj.applications.count()
    application_count.short_description = 'Applications'

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ['applicant', 'job', 'status', 'applied_at']
    list_filter = ['status', 'applied_at', 'job__company']
    search_fields = ['applicant__username', 'job__title', 'cover_letter']
    readonly_fields = ['applied_at']
    date_hierarchy = 'applied_at'
    
    fieldsets = (
        ('Application Info', {
            'fields': ('job', 'applicant', 'status', 'applied_at')
        }),
        ('Application Content', {
            'fields': ('cover_letter', 'resume')
        }),
    )
