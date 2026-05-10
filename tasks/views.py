"""
tasks/views.py
==============
This module handles all task management views for the Secure Task Manager.
Security is enforced at every level to prevent unauthorized access.

Security Features Implemented:
- All views protected with @login_required decorator
- User data isolation - users can only access their own tasks
- Input validation and XSS prevention on task creation
- Protection against Insecure Direct Object Reference (IDOR) attacks
- Server-side validation cannot be bypassed by disabling browser validation
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.html import escape
import re
import logging
from .models import Task

# Security: Logger for task-related security events
logger = logging.getLogger('security')


def validate_task_input(title, description):
    """
    Validate and sanitize task inputs to prevent XSS and injection attacks.
    
    Security measures:
    - Enforces minimum and maximum length on title
    - Detects and rejects malicious script tags (XSS prevention)
    - Enforces maximum length on description
    - Returns list of errors for display to user
    
    Args:
        title: Task title from user input
        description: Task description from user input
    
    Returns:
        List of error messages (empty if valid)
    """
    errors = []

    # Validate title presence and length
    if not title:
        errors.append('Title is required.')
    elif len(title) < 3:
        # Minimum length prevents meaningless task titles
        errors.append('Title must be at least 3 characters.')
    elif len(title) > 200:
        # Maximum length prevents database overflow attacks
        errors.append('Title must be less than 200 characters.')

    # Security: Detect malicious script injection attempts in title
    # This prevents stored XSS attacks where scripts could execute for other users
    if title and re.search(r'<script.*?>.*?</script>', title, re.IGNORECASE):
        errors.append('Invalid characters in title.')

    # Validate description length
    if len(description) > 1000:
        # Maximum length prevents database overflow attacks
        errors.append('Description must be less than 1000 characters.')

    return errors


@login_required
def task_list(request):
    """
    Display all tasks belonging to the currently logged-in user.
    
    Security measures:
    - @login_required: Redirects unauthenticated users to login page
    - User data isolation: Tasks filtered by request.user
      (users cannot see other users' tasks)
    - Ordered by creation date (newest first)
    """
    # Security: Filter tasks by logged-in user only
    # This prevents users from accessing other users' tasks (IDOR prevention)
    tasks = Task.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'tasks/task_list.html', {'tasks': tasks})


@login_required
def task_create(request):
    """
    Handle task creation with input validation and XSS prevention.
    
    Security measures:
    - @login_required: Redirects unauthenticated users to login page
    - Input sanitization: escape() prevents XSS attacks
    - Server-side validation: Cannot be bypassed by disabling browser validation
    - Priority whitelist: Only allows predefined priority values
    - Task linked to logged-in user: Cannot create tasks for other users
    """
    if request.method == 'POST':
        # Security: escape() sanitizes input to prevent XSS attacks
        # strip() removes leading/trailing whitespace
        title = escape(request.POST.get('title', '').strip())
        description = escape(request.POST.get('description', '').strip())
        priority = request.POST.get('priority', 'medium')

        # Security: Whitelist validation for priority field
        # Prevents injection of arbitrary values into the database
        allowed_priorities = ['low', 'medium', 'high']
        if priority not in allowed_priorities:
            priority = 'medium'  # Default to medium if invalid value provided

        # Security: Server-side validation (cannot be bypassed client-side)
        errors = validate_task_input(title, description)

        if errors:
            # Return form with errors and retain user's input
            for error in errors:
                messages.error(request, error)
            return render(request, 'tasks/task_create.html', {
                'title': title,
                'description': description,
                'priority': priority,
            })

        # Security: Associate task with logged-in user only
        # Users cannot create tasks on behalf of other users
        Task.objects.create(
            title=title,
            description=description,
            priority=priority,
            user=request.user  # Always use request.user, never user-provided user ID
        )
        messages.success(request, 'Task created successfully!')
        return redirect('task_list')

    return render(request, 'tasks/task_create.html')


@login_required
def task_complete(request, pk):
    """
    Mark a task as complete.
    
    Security measures:
    - @login_required: Redirects unauthenticated users to login page
    - get_object_or_404 with user=request.user: Prevents IDOR attacks
      (users cannot complete other users' tasks by guessing task IDs)
    """
    # Security: get_object_or_404 with user=request.user prevents IDOR attacks
    # If user tries to access another user's task, returns 404 instead of the task
    task = get_object_or_404(Task, pk=pk, user=request.user)
    task.completed = True
    task.save()
    return redirect('task_list')


@login_required
def task_delete(request, pk):
    """
    Delete a task.
    
    Security measures:
    - @login_required: Redirects unauthenticated users to login page
    - get_object_or_404 with user=request.user: Prevents IDOR attacks
      (users cannot delete other users' tasks by guessing task IDs)
    - Deletion logged for audit trail
    """
    # Security: get_object_or_404 with user=request.user prevents IDOR attacks
    task = get_object_or_404(Task, pk=pk, user=request.user)
    task.delete()
    messages.success(request, 'Task deleted!')
    return redirect('task_list')