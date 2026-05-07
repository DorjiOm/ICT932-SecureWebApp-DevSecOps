from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

@login_required
def home(request):
    if request.user.is_staff:
        return render(request, 'admin_home.html')
    else:
        return render(request, 'user_home.html')