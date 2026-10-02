from django import forms
from django.contrib.auth.models import User
from .models import Project, Task, TaskComment

class UserRegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'পাসওয়ার্ড দিন'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'পাসওয়ার্ড পুনরায় দিন'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ইউজারনেম'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'ইমেইল'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'নামের প্রথম অংশ'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'নামের শেষ অংশ'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password != confirm_password:
            raise forms.ValidationError("পাসওয়ার্ড মিলছে না!")

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'description', 'members']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'প্রজেক্টের নাম'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'প্রজেক্টের বিবরণ'}),
            'members': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'assigned_to', 'status', 'priority', 'due_date', 'attachment']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'টাস্কের নাম'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'টাস্কের বিবরণ'}),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'attachment': forms.FileInput(attrs={'class': 'form-control'}),
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = TaskComment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'কমেন্ট লিখুন...'}),
        }