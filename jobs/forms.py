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

class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['cover_letter', 'resume']
        widgets = {
            'cover_letter': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 6,
                'placeholder': 'Write a compelling cover letter explaining why you\'re interested in this position and how your skills match the requirements...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['resume'].widget.attrs.update({
            'class': 'form-control',
            'accept': '.pdf,.doc,.docx'
        })
        self.fields['resume'].help_text = 'Upload your resume (PDF, DOC, DOCX) - Max 5MB'
    
    def clean_resume(self):
        resume = self.cleaned_data.get('resume')
        if resume:
            # Check file size (5MB limit)
            if resume.size > 5 * 1024 * 1024:
                raise forms.ValidationError('Resume file size must be under 5MB.')
            
            # Check file extension
            allowed_extensions = ['.pdf', '.doc', '.docx']
            file_extension = resume.name.lower()
            if not any(file_extension.endswith(ext) for ext in allowed_extensions):
                raise forms.ValidationError('Please upload a PDF, DOC, or DOCX file.')
        
        return resume
