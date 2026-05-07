from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Task

# Show all tasks for logged in user
@login_required
def task_list(request):
    tasks = Task.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'tasks/task_list.html', {'tasks': tasks})

# Create a new task
@login_required
def task_create(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        priority = request.POST.get('priority')
        # Security: associate task with logged in user only
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