"""
accounts/models.py
==================
This module defines the Profile model which extends Django's built-in
User model to support Role-Based Access Control (RBAC).

Security Features:
- Two roles: Admin and User with different access levels
- Profile automatically created for every new user via Django signals
- Role check method prevents unauthorized access to admin features
"""

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    """
    Extends Django's User model with role-based access control.
    
    Security Design:
    - Uses OneToOneField to ensure one profile per user
    - Default role is 'user' (least privilege principle)
    - Admin role must be explicitly assigned by superuser
    - is_admin() method used throughout app for access control
    """

    ADMIN_ROLE = 'admin'
    USER_ROLE = 'user'
    ROLE_CHOICES = [
        (ADMIN_ROLE, 'Admin'),
        (USER_ROLE, 'User'),
        ]

    # Security: OneToOne ensures each user has exactly one profile
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # Security: Default role is 'user' (principle of least privilege)
    # Admin role must be explicitly granted
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=USER_ROLE)

    def __str__(self):
        return f'{self.user.username} - {self.role}'

    def is_admin(self):
        """
        Check if user has admin role.
        Used throughout the app to enforce RBAC.
        
        Returns:
            bool: True if user is admin, False otherwise
        """
        return self.role == self.ADMIN_ROLE


# Security: Automatically create Profile when new User is created
# This ensures every user has a role assigned (default: 'user')
@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    """Create a Profile for every newly registered user."""
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    """Save profile when user is saved. Creates profile if missing."""
    # Security: get_or_create handles existing users without profiles
    Profile.objects.get_or_create(user=instance)
    instance.profile.save()