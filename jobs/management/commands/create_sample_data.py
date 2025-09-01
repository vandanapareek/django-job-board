from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from jobs.models import Profile, Job
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = 'Create sample data for the job board'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')

        # Create sample users
        users_data = [
            {'username': 'techcorp', 'email': 'hr@techcorp.com', 'role': 'company'},
            {'username': 'innovate_inc', 'email': 'careers@innovate.com', 'role': 'company'},
            {'username': 'startup_xyz', 'email': 'jobs@startupxyz.com', 'role': 'company'},
            {'username': 'john_doe', 'email': 'john@example.com', 'role': 'user'},
            {'username': 'jane_smith', 'email': 'jane@example.com', 'role': 'user'},
        ]

        for user_data in users_data:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={'email': user_data['email']}
            )
            if created:
                user.set_password('password123')
                user.save()
                # Update profile role
                profile = user.profile
                profile.role = user_data['role']
                profile.save()
                self.stdout.write(f'Created user: {user.username} ({user_data["role"]})')

        # Create sample jobs
        jobs_data = [
            {
                'title': 'Senior Python Developer',
                'company_username': 'techcorp',
                'location': 'San Francisco, CA',
                'description': '''We are looking for an experienced Python developer to join our growing team. 

Responsibilities:
- Develop and maintain web applications using Django
- Collaborate with cross-functional teams
- Write clean, maintainable code
- Participate in code reviews

Requirements:
- 5+ years of Python development experience
- Strong knowledge of Django framework
- Experience with databases (PostgreSQL preferred)
- Excellent problem-solving skills''',
                'apply_link': 'https://techcorp.com/careers/python-developer',
                'days_ago': 2
            },
            {
                'title': 'Frontend React Developer',
                'company_username': 'innovate_inc',
                'location': 'New York, NY',
                'description': '''Join our innovative team as a Frontend React Developer!

What you'll do:
- Build responsive user interfaces with React
- Work with modern JavaScript (ES6+)
- Collaborate with designers and backend developers
- Optimize application performance

What we're looking for:
- 3+ years of React development experience
- Proficiency in HTML, CSS, and JavaScript
- Experience with state management (Redux/Context)
- Strong attention to detail''',
                'apply_link': 'https://innovate.com/jobs/react-developer',
                'days_ago': 5
            },
            {
                'title': 'DevOps Engineer',
                'company_username': 'startup_xyz',
                'location': 'Remote',
                'description': '''We're a fast-growing startup looking for a DevOps Engineer to help us scale our infrastructure.

Key responsibilities:
- Manage cloud infrastructure (AWS/Azure/GCP)
- Implement CI/CD pipelines
- Monitor system performance and security
- Automate deployment processes

Requirements:
- 3+ years of DevOps experience
- Experience with Docker and Kubernetes
- Knowledge of cloud platforms
- Strong scripting skills (Python/Bash)''',
                'apply_link': 'https://startupxyz.com/careers/devops',
                'days_ago': 1
            },
            {
                'title': 'Data Scientist',
                'company_username': 'techcorp',
                'location': 'Austin, TX',
                'description': '''Exciting opportunity for a Data Scientist to join our analytics team!

You will:
- Analyze large datasets to extract insights
- Build machine learning models
- Present findings to stakeholders
- Collaborate with engineering teams

Requirements:
- MS/PhD in Statistics, Computer Science, or related field
- Experience with Python (pandas, scikit-learn, TensorFlow)
- Strong statistical analysis skills
- Excellent communication abilities''',
                'apply_link': 'https://techcorp.com/careers/data-scientist',
                'days_ago': 3
            },
            {
                'title': 'Product Manager',
                'company_username': 'innovate_inc',
                'location': 'Boston, MA',
                'description': '''We're seeking a Product Manager to drive product strategy and execution.

Responsibilities:
- Define product vision and roadmap
- Work with engineering and design teams
- Analyze market trends and user feedback
- Prioritize features and requirements

Requirements:
- 4+ years of product management experience
- Strong analytical and strategic thinking
- Excellent communication and leadership skills
- Experience with agile methodologies''',
                'apply_link': 'https://innovate.com/jobs/product-manager',
                'days_ago': 7
            }
        ]

        for job_data in jobs_data:
            company = User.objects.get(username=job_data['company_username'])
            posted_at = timezone.now() - timedelta(days=job_data['days_ago'])
            
            job, created = Job.objects.get_or_create(
                title=job_data['title'],
                company=company,
                defaults={
                    'location': job_data['location'],
                    'description': job_data['description'],
                    'apply_link': job_data['apply_link'],
                    'posted_at': posted_at
                }
            )
            
            if created:
                self.stdout.write(f'Created job: {job.title} at {job.company.username}')

        self.stdout.write(
            self.style.SUCCESS('Successfully created sample data!')
        )
        self.stdout.write('\nSample users created:')
        self.stdout.write('- techcorp (company) - password: password123')
        self.stdout.write('- innovate_inc (company) - password: password123')
        self.stdout.write('- startup_xyz (company) - password: password123')
        self.stdout.write('- john_doe (user) - password: password123')
        self.stdout.write('- jane_smith (user) - password: password123')
        self.stdout.write('\nAdmin user: admin - password: admin123')
