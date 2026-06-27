# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models
from datetime import timedelta
from django.utils import timezone


class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    profile_photo = models.ImageField(upload_to='profiles/', blank=True, null=True)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    daily_transfer_limit = models.DecimalField(max_digits=15, decimal_places=2, default=10000.00)
    transaction_pin = models.CharField(max_length=4, blank=True)
    account_number = models.CharField(max_length=20, unique=True, blank=True)
    is_verified = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email


class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('transfer', 'Transfer'),
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    TRANSFER_TYPES = [
        ('domestic', 'Domestic Transfer'),
        ('wire', 'Wire Transfer'),
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
    ]

    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='sent_transactions')
    recipient_name = models.CharField(max_length=100)
    recipient_email = models.EmailField(blank=True)
    recipient_bank = models.CharField(max_length=100)
    recipient_account = models.CharField(max_length=20)
    swift_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    transfer_type = models.CharField(max_length=20, choices=TRANSFER_TYPES, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    reference = models.CharField(max_length=50, unique=True, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # ========== NEW CURRENCY FIELDS ==========
    equivalent_amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    target_currency = models.CharField(max_length=10, blank=True, null=True)
    currency_symbol = models.CharField(max_length=5, blank=True, null=True)

    def __str__(self):
        return f"{self.sender} - {self.amount} - {self.status}"


class SystemSettings(models.Model):
    """Admin controls for all security features"""
    pending_approval_enabled = models.BooleanField(default=False, help_text="Require admin approval for transfers")
    otp_enabled = models.BooleanField(default=False, help_text="Require OTP verification for transfers")
    imf_enabled = models.BooleanField(default=False, help_text="Require IMF code for transfers")
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "System Settings"
    
    def __str__(self):
        status = []
        if self.pending_approval_enabled:
            status.append("Pending")
        if self.otp_enabled:
            status.append("OTP")
        if self.imf_enabled:
            status.append("IMF")
        return f"Settings: {', '.join(status) if status else 'All OFF'}"


class OTP(models.Model):
    """One-Time Password for transfer verification"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
    transaction_id = models.IntegerField(null=True, blank=True)
    
    def is_expired(self):
        """Check if OTP is older than 5 minutes"""
        return self.created_at < timezone.now() - timedelta(minutes=5)
    
    def __str__(self):
        return f"{self.user.email} - {self.code} - {'Used' if self.is_used else 'Active'}"


class IMF(models.Model):
    """International Monetary Fund code - Permanent user code"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=50, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.email} - {self.code}"


class AccountRestriction(models.Model):
    """Restrict specific users from making transfers"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_restricted = models.BooleanField(default=False, help_text="Restrict this user from making transfers")
    reason = models.TextField(blank=True, help_text="Reason for restriction")
    restricted_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.email} - {'Restricted' if self.is_restricted else 'Active'}"


class UserSecuritySettings(models.Model):
    """Per-user security settings - each user has their own settings"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='security_settings')
    pending_approval_enabled = models.BooleanField(default=False, help_text="Require admin approval for this user's transfers")
    otp_enabled = models.BooleanField(default=True, help_text="Require OTP verification for this user's transfers")
    imf_enabled = models.BooleanField(default=False, help_text="Require IMF code for this user's transfers")
    manual_verification_enabled = models.BooleanField(default=False, help_text="Require manual verification after transfer (receipt shows pending)")
    is_restricted = models.BooleanField(default=False, help_text="Restrict this user from making transfers")
    restriction_reason = models.TextField(blank=True, help_text="Reason for restriction (shown to user)")
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "User Security Setting"
        verbose_name_plural = "User Security Settings"
    
    def __str__(self):
        status = []
        if self.pending_approval_enabled:
            status.append("Pending")
        if self.otp_enabled:
            status.append("OTP")
        if self.imf_enabled:
            status.append("IMF")
        if self.manual_verification_enabled:
            status.append("Manual Verification")
        if self.is_restricted:
            status.append("RESTRICTED")
        return f"{self.user.email} - {', '.join(status) if status else 'All OFF'}"