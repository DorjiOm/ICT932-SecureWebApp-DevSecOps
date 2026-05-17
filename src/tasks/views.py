from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout

@login_required
def home(request):
    if request.user.is_staff:
        return render(request, 'admin_home.html')
    else:
        return render(request, 'user_home.html')

def custom_logout(request):
    logout(request)
    return redirect('/login/')