from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.conf import settings
import secrets
import string
import uuid


class User(AbstractUser):
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    contact_number = models.CharField(max_length=20)
    date_of_birth = models.DateField()
    address_line = models.CharField(max_length=255)
    barangay = models.CharField(max_length=100, default="Labangon")
    city = models.CharField(max_length=100, default="Cebu City")
    province = models.CharField(max_length=100, default="Cebu")
    postal_code = models.CharField(max_length=10, default="6000")

    # UPDATED: Changed from BinaryField to URLField for Supabase Storage

    profile_photo_url = models.URLField(blank=True, null=True)
    resident_id_photo_url = models.URLField(blank=True, null=True)

    resident_confirmation = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    
    REQUIRED_FIELDS = ["email", "full_name", "contact_number", "date_of_birth"]
    civil_status = models.CharField(max_length=20, blank=True, null=True, choices=[
        ('Single','Single'), ('Married','Married'), ('Widowed','Widowed'), ('Separated','Separated'),
    ])

    def __str__(self):
        return self.username


class PasswordResetCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    
    @classmethod
    def generate_code(cls, user):
        """Generate a new 6-digit verification code for the user"""
        # Delete any existing unused codes for this user
        cls.objects.filter(user=user, is_used=False).delete()
        
        # Generate a 6-digit code
        code = ''.join(secrets.choice(string.digits) for _ in range(6))
        
        # Create the reset code (expires in 5 minutes)
        from django.utils import timezone
        expires_at = timezone.now() + timezone.timedelta(minutes=5)
        
        return cls.objects.create(
            user=user,
            code=code,
            expires_at=expires_at
        )
    
    def is_valid(self):
        """Check if the code is still valid (not expired and not used)"""
        from django.utils import timezone
        return not self.is_used and timezone.now() < self.expires_at
    
    def __str__(self):
        return f"Reset code for {self.user.email}: {self.code}"





