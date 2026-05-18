from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from phonenumber_field.modelfields import PhoneNumberField
from django_countries.fields import CountryField
import uuid

class User(AbstractUser):
    ROLE_CHOICES = [
        ('client', 'Client'),
        ('freelancer', 'Freelancer'),
        ('admin', 'Admin'),
        ('moderator', 'Moderator'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='client')
    email = models.EmailField(unique=True)
    phone = PhoneNumberField(blank=True, null=True)
    country = CountryField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    
    # Verification
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)
    identity_verified = models.BooleanField(default=False)
    
    # Profile
    bio = models.TextField(max_length=500, blank=True)
    skills = models.JSONField(default=list, blank=True)
    headline = models.CharField(max_length=200, blank=True)
    
    # Statistics
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    total_reviews = models.IntegerField(default=0)
    completed_orders = models.IntegerField(default=0)
    total_earned = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Security
    is_suspended = models.BooleanField(default=False)
    suspension_reason = models.TextField(blank=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    
    # Gamification
    level = models.IntegerField(default=1)
    xp_points = models.IntegerField(default=0)
    
    # ========== OTP FIELDS (YEH ADD KARO) ==========
    otp_code = models.CharField(max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(blank=True, null=True)
    otp_purpose = models.CharField(max_length=20, blank=True, null=True)  # 'reset' or 'verify'
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    def __str__(self):
        if self.get_full_name():
            return self.get_full_name()
        if self.username:
            return self.username
        return self.email.split('@')[0]
    
    @property
    def is_freelancer(self):
        return self.role == 'freelancer'
    
    @property
    def is_client(self):
        return self.role == 'client'

class EmailVerificationToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.email} - {self.token}"

class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.user.email} - {self.token}"