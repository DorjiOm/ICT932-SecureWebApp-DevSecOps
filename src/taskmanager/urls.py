from django.contrib import admin
from django.urls import path, include
from tasks import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('django.contrib.auth.urls')),
    path('', views.home, name='home'),
]