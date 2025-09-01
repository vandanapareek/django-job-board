# Django Job Board - Beginner's Development Guide

## 🚀 Complete Step-by-Step Development Process

### Phase 1: Environment Setup

#### 1.1 Create Project Directory
```bash
cd /Users/vandana/pyhton-project
mkdir jobboard-project
cd jobboard-project
```

#### 1.2 Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
```

#### 1.3 Install Django
```bash
pip install django
pip freeze > requirements.txt
```

### Phase 2: Django Project Structure

#### 2.1 Create Django Project
```bash
django-admin startproject jobboard .
```

#### 2.2 Create Django App
```bash
python manage.py startapp jobs
```

#### 2.3 Add App to Settings
**File: `jobboard/settings.py`**
```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'jobs',  # Add this line
]
```

### Phase 3: Database Models

#### 3.1 Create Models
**File: `jobs/models.py`**
```python
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('company', 'Company'),
        ('user', 'User'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')

class Job(models.Model):
    title = models.CharField(max_length=200)
    company = models.ForeignKey(User, on_delete=models.CASCADE)
    location = models.CharField(max_length=100)
    description = models.TextField()
    posted_at = models.DateTimeField(auto_now_add=True)

class Application(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    applicant = models.ForeignKey(User, on_delete=models.CASCADE)
    cover_letter = models.TextField()
    resume = models.FileField(upload_to='resumes/')
    applied_at = models.DateTimeField(auto_now_add=True)
```

#### 3.2 Create Database Tables
```bash
python manage.py makemigrations
python manage.py migrate
```

### Phase 4: User Authentication

#### 4.1 Create Superuser
```bash
python manage.py createsuperuser
# Username: admin
# Password: admin123
```

#### 4.2 Configure Authentication Settings
**File: `jobboard/settings.py`**
```python
LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/login/'
LOGOUT_REDIRECT_URL = '/'
```

### Phase 5: Forms

#### 5.1 Create Forms
**File: `jobs/forms.py`**
```python
from django import forms
from .models import Job, Application

class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['title', 'location', 'description']

class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['cover_letter', 'resume']
```

### Phase 6: Views (Business Logic)

#### 6.1 Create Views
**File: `jobs/views.py`**
```python
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Job, Application
from .forms import JobForm, ApplicationForm

def job_list(request):
    jobs = Job.objects.all()
    return render(request, 'jobs/job_list.html', {'jobs': jobs})

@login_required
def add_job(request):
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.company = request.user
            job.save()
            return redirect('jobs:job_list')
    else:
        form = JobForm()
    return render(request, 'jobs/job_form.html', {'form': form})
```

### Phase 7: URLs (Routing)

#### 7.1 Main URLs
**File: `jobboard/urls.py`**
```python
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('jobs.urls')),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]
```

#### 7.2 App URLs
**File: `jobs/urls.py`**
```python
from django.urls import path
from . import views

app_name = 'jobs'

urlpatterns = [
    path('', views.job_list, name='job_list'),
    path('add/', views.add_job, name='add_job'),
]
```

### Phase 8: Templates (Frontend)

#### 8.1 Create Template Directories
```bash
mkdir templates
mkdir templates/jobs
mkdir templates/registration
```

#### 8.2 Base Template
**File: `templates/base.html`**
```html
<!DOCTYPE html>
<html>
<head>
    <title>Job Board</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="{% url 'jobs:job_list' %}">Job Board</a>
            <div class="navbar-nav ms-auto">
                {% if user.is_authenticated %}
                    <a class="nav-link" href="{% url 'logout' %}">Logout</a>
                {% else %}
                    <a class="nav-link" href="{% url 'login' %}">Login</a>
                {% endif %}
            </div>
        </div>
    </nav>
    
    <div class="container mt-4">
        {% block content %}
        {% endblock %}
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
```

#### 8.3 Job List Template
**File: `templates/jobs/job_list.html`**
```html
{% extends 'base.html' %}

{% block content %}
<h1>Available Jobs</h1>
<div class="row">
    {% for job in jobs %}
    <div class="col-md-6 mb-4">
        <div class="card">
            <div class="card-body">
                <h5 class="card-title">{{ job.title }}</h5>
                <p class="card-text">{{ job.description }}</p>
                <p class="card-text"><small class="text-muted">{{ job.location }}</small></p>
            </div>
        </div>
    </div>
    {% endfor %}
</div>
{% endblock %}
```

### Phase 9: Admin Interface

#### 9.1 Configure Admin
**File: `jobs/admin.py`**
```python
from django.contrib import admin
from .models import Profile, Job, Application

admin.site.register(Profile)
admin.site.register(Job)
admin.site.register(Application)
```

### Phase 10: Static Files

#### 10.1 Configure Static Files
**File: `jobboard/settings.py`**
```python
STATICFILES_DIRS = [BASE_DIR / 'static']
```

#### 10.2 Create Static Directory
```bash
mkdir static
mkdir static/css
```

### Phase 11: Run the Project

#### 11.1 Start Development Server
```bash
python manage.py runserver
```

#### 11.2 Access the Application
- Open browser to: http://127.0.0.1:8000/
- Admin panel: http://127.0.0.1:8000/admin/

## 🔧 Key Concepts Explained

### 1. **MVC Pattern**
- **Model**: Database structure (`models.py`)
- **View**: Business logic (`views.py`)
- **Template**: Display (`templates/`)

### 2. **URL Routing**
- Maps web addresses to functions
- Handles URL parameters

### 3. **Forms**
- Handle user input
- Validate data before saving

### 4. **Authentication**
- User login/logout
- Role-based access control

### 5. **Admin Interface**
- Built-in data management
- Automatic CRUD operations

## 🚨 Common Issues & Solutions

### Issue 1: "django-admin not found"
```bash
source venv/bin/activate
pip install django
```

### Issue 2: Login redirects to wrong URL
Add to `settings.py`:
```python
LOGIN_REDIRECT_URL = '/'
```

### Issue 3: Static files not loading
Add to `settings.py`:
```python
STATICFILES_DIRS = [BASE_DIR / 'static']
```

### Issue 4: Database errors
```bash
python manage.py makemigrations
python manage.py migrate
```

## 📁 Final Project Structure
```
jobboard-project/
├── venv/
├── jobboard/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── jobs/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── forms.py
│   └── admin.py
├── templates/
│   ├── base.html
│   └── jobs/
│       └── job_list.html
├── static/
├── manage.py
└── requirements.txt
```

## 🎯 Next Steps

1. **Add more features**: Search, filtering, pagination
2. **Improve styling**: Custom CSS, better UI/UX
3. **Add tests**: Unit tests, integration tests
4. **Deploy**: Deploy to production server
5. **Security**: Add CSRF protection, input validation

This guide covers the complete development process from scratch to a working job board application!
