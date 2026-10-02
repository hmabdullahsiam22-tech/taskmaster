from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Project, Task
from .forms import UserRegisterForm, ProjectForm, TaskForm

# ১. ইউজার রেজিস্ট্রেশন
def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user)
            messages.success(request, 'আপনার অ্যাকাউন্ট সফলভাবে তৈরি হয়েছে!')
            return redirect('dashboard')
    else:
        form = UserRegisterForm()
    return render(request, 'core/register.html', {'form': form})

# ২. ইউজার লগইন
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'ভুল ইউজারনেম বা পাসওয়ার্ড দেওয়া হয়েছে!')
    else:
        form = AuthenticationForm()
    return render(request, 'core/login.html', {'form': form})

# ৩. ইউজার লগআউট
def logout_view(request):
    logout(request)
    return redirect('login')

# ৪. ড্যাশবোর্ড / প্রজেক্ট লিস্ট
@login_required
def dashboard(request):
    projects = Project.objects.filter(owner=request.user) | Project.objects.filter(members=request.user)
    projects = projects.distinct()
    return render(request, 'core/dashboard.html', {'projects': projects})

# ৫. নতুন প্রজেক্ট তৈরি
@login_required
def create_project(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            form.save_m2m() # সদস্য যোগ করার জন্য
            messages.success(request, 'নতুন প্রজেক্ট সফলভাবে তৈরি হয়েছে!')
            return redirect('dashboard')
    else:
        form = ProjectForm()
    return render(request, 'core/project_form.html', {'form': form, 'title': 'নতুন প্রজেক্ট তৈরি করুন'})

# ৬. প্রজেক্টের কানবান বোর্ড ও টাস্ক লিস্ট
@login_required
def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    
    # অনুমতি পরীক্ষা
    if project.owner != request.user and request.user not in project.members.all():
        messages.error(request, 'আপনার এই প্রজেক্ট দেখার অনুমতি নেই!')
        return redirect('dashboard')

    tasks = project.tasks.all()
    
    context = {
        'project': project,
        'todo_tasks': tasks.filter(status='todo'),
        'in_progress_tasks': tasks.filter(status='in_progress'),
        'review_tasks': tasks.filter(status='review'),
        'done_tasks': tasks.filter(status='done'),
    }
    return render(request, 'core/project_detail.html', context)

# ৭. প্রজেক্টে নতুন টাস্ক তৈরি
@login_required
def create_task(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if request.method == 'POST':
        form = TaskForm(request.POST, request.FILES)
        if form.is_valid():
            task = form.save(commit=False)
            task.project = project
            task.save()
            messages.success(request, 'টাস্ক সফলভাবে তৈরি হয়েছে!')
            return redirect('project_detail', pk=project.id)
    else:
        form = TaskForm()
        # শুধু প্রজেক্টের মেম্বারদের অ্যাসাইন করার অপশন রাখা
        form.fields['assigned_to'].queryset = project.members.all() | User.objects.filter(id=project.owner.id)
    return render(request, 'core/task_form.html', {'form': form, 'project': project})

# ৮. টাস্কের বিস্তারিত বিবরণ ও কমেন্ট সেকশন
@login_required
def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk)
    comments = task.comments.all().order_by('-created_at')
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.task = task
            comment.author = request.user
            comment.save()
            return redirect('task_detail', pk=task.id)
    else:
        form = CommentForm()
        
    return render(request, 'core/task_detail.html', {'task': task, 'comments': comments, 'form': form})

# ৯. টাস্কের স্ট্যাটাস আপডেট করা
@login_required
def update_task_status(request, pk, status):
    task = get_object_or_404(Task, pk=pk)
    if status in ['todo', 'in_progress', 'review', 'done']:
        task.status = status
        task.save()
    return redirect('project_detail', pk=task.project.id)