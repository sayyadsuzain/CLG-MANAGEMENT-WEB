from django import forms
from django.core.validators import EmailValidator
from .models import User, Student, Course, Assignment, Resource, Notice

class LoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter your password'})
    )

class PasswordChangeForm(forms.Form):
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter your current password'})
    )
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter new password'}),
        min_length=8
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm new password'})
    )

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')

        if new_password and confirm_password:
            if new_password != confirm_password:
                raise forms.ValidationError("Passwords do not match")
        return cleaned_data

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['student_id', 'department', 'semester', 'roll_number']
        widgets = {
            'student_id': forms.TextInput(attrs={'class': 'form-control'}),
            'department': forms.TextInput(attrs={'class': 'form-control'}),
            'semester': forms.NumberInput(attrs={'class': 'form-control'}),
            'roll_number': forms.TextInput(attrs={'class': 'form-control'})
        }

class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['title', 'description', 'file', 'due_date', 'max_marks']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
            'due_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'max_marks': forms.NumberInput(attrs={'class': 'form-control'})
        }

class ResourceForm(forms.ModelForm):
    class Meta:
        model = Resource
        fields = ['title', 'description', 'file']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'file': forms.FileInput(attrs={'class': 'form-control'})
        }

class NoticeForm(forms.ModelForm):
    class Meta:
        model = Notice
        fields = ['title', 'content', 'priority', 'course']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'course': forms.Select(attrs={'class': 'form-control'})
        }

class BulkStudentUploadForm(forms.Form):
    file = forms.FileField(
        widget=forms.FileInput(attrs={'class': 'form-control'}),
        help_text='Upload a CSV file with student details'
    )
    course = forms.ModelChoiceField(
        queryset=Course.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )

class PasswordResetForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email address'}),
        validators=[EmailValidator()],
        help_text='Enter the email address you used to register.'
    )

class SetPasswordForm(forms.Form):
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter new password'}),
        min_length=8,
        help_text='Your password must be at least 8 characters long.'
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm new password'})
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')

        if new_password and confirm_password:
            if new_password != confirm_password:
                raise forms.ValidationError("Passwords do not match")
        return cleaned_data

    def save(self):
        password = self.cleaned_data["new_password"]
        self.user.set_password(password)
        self.user.save()
        return self.user 