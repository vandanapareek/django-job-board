from django.urls import path
from . import views

app_name = 'jobs'

urlpatterns = [
    path('', views.job_list, name='job_list'),
    path('<int:job_id>/', views.job_detail, name='job_detail'),
    path('<int:job_id>/apply/', views.apply_job, name='apply_job'),
    path('applications/', views.my_applications, name='my_applications'),
    path('applications/<int:application_id>/', views.application_detail, name='application_detail'),
    path('company/applications/', views.company_applications, name='company_applications'),
    path('applications/<int:application_id>/update-status/', views.update_application_status, name='update_application_status'),
    path('add/', views.add_job, name='add_job'),
    path('<int:job_id>/edit/', views.edit_job, name='edit_job'),
    path('<int:job_id>/delete/', views.delete_job, name='delete_job'),
]
