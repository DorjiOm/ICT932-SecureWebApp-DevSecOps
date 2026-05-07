from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.html import escape
import re
from .models import Task

# Security: Input validation helper functions
def validate_task_input(title, description):
    """Validate and sanitize task inputs to prevent XSS and bad data"""
    errors = []
    
    # Validate title
    if not title:
        errors.append('Title is required.')
    elif len(title) < 3:
        errors.append('Title must be at least 3 characters.')
    elif len(title) > 200:
        errors.append('Title must be less than 200 characters.')
    
    # Security: Check for malicious script tags in title
    if re.search(r'<script.*?>.*?</script>', title, re.IGNORECASE):
        errors.append('Invalid characters in title.')
    
    # Validate description
    if len(description) > 1000:
        errors.append('Description must be less than 1000 characters.')
    
    return errors

# Show all tasks for logged in user
@login_required
def task_list(request):
    # Security: Only show tasks belonging to the logged in user
    tasks = Task.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'tasks/task_list.html', {'tasks': tasks})

# Create a new task
@login_required
def task_create(request):
    if request.method == 'POST':
        # Security: Escape input to prevent XSS
        title = escape(request.POST.get('title', '').strip())
        description = escape(request.POST.get('description', '').strip())
        priority = request.POST.get('priority', 'medium')
        
        # Security: Validate priority is one of allowed values
        allowed_priorities = ['low', 'medium', 'high']
        if priority not in allowed_priorities:
            priority = 'medium'
        
        # Security: Validate all inputs before saving
        errors = validate_task_input(title, description)
        
        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'tasks/task_create.html', {
                'title': title,
                'description': description,
                'priority': priority,
            })
        
        # Security: Associate task with logged in user only
        Task.objects.create(
            title=title,
            description=description,
            priority=priority,
            user=request.user
        )
        messages.success(request, 'Task created successfully!')
        return redirect('task_list')
    return render(request, 'tasks/task_create.html')

# Mark task as complete
@login_required
def task_complete(request, pk):
    # Security: only allow user to complete their own tasks
    task = get_object_or_404(Task, pk=pk, user=request.user)
    task.completed = True
    task.save()
    return redirect('task_list')

# Delete a task
@login_required
def task_delete(request, pk):
    # Security: only allow user to delete their own tasks
    task = get_object_or_404(Task, pk=pk, user=request.user)
    task.delete()
    messages.success(request, 'Task deleted!')
    return redirect('task_list')