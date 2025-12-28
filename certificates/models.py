from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid


class CertificateRequest(models.Model):
    CERTIFICATE_TYPES = [
        ('barangay_clearance', 'Barangay Clearance'),
        ('residency', 'Certificate of Residency'),
        ('indigency', 'Certificate of Indigency'),
        ('good_moral', 'Good Moral Character'),
        ('business_clearance', 'Business Clearance'),
    ]
    
    PAYMENT_STATUS = [
        ('unpaid', 'Unpaid'),
        ('pending', 'Pending Verification'),
        ('paid', 'Paid'),
        ('failed', 'Failed Payment Verification'),
    ]
    
    PAYMENT_MODE = [
        ('gcash', 'GCash'),
        ('counter', 'Pay-on-the-Counter'),
    ]
    
    CLAIM_STATUS = [
        ('processing', 'Processing'),
        ('ready', 'Ready for Claim'),
        ('claimed', 'Claimed'),
        ('failed', 'Failed'),
    ]
    
    # Basic Info
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Change from 'User' to 'settings.AUTH_USER_MODEL'
        on_delete=models.CASCADE, 
        related_name='certificate_requests'
    )
    request_id = models.CharField(max_length=20, unique=True, editable=False)
    certificate_type = models.CharField(max_length=50, choices=CERTIFICATE_TYPES)
    
    # Request Details
    purpose = models.TextField()
    proof_photo_url = models.URLField(blank=True, null=True)
    
    # Business Details
    business_name = models.CharField(max_length=255, blank=True, null=True)
    business_type = models.CharField(max_length=50, blank=True, null=True)
    business_nature = models.CharField(max_length=255, blank=True, null=True)
    business_address = models.TextField(blank=True, null=True)
    employees_count = models.PositiveIntegerField(blank=True, null=True)
    
    # Payment Info
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='unpaid')
    payment_mode = models.CharField(max_length=20, choices=PAYMENT_MODE, blank=True, null=True)
    payment_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_reference = models.CharField(max_length=50, blank=True, null=True)
    
    # Claim Status
    claim_status = models.CharField(max_length=20, choices=CLAIM_STATUS, default='processing')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid_at = models.DateTimeField(blank=True, null=True)
    claimed_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['payment_status']),
            models.Index(fields=['certificate_type']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.request_id:
            # Generate unique request ID (e.g., REQ-2025-0001)
            import random
            year = timezone.now().year
            
            # Try to generate a unique request ID with retry logic
            max_attempts = 100
            for attempt in range(max_attempts):
                # Get the highest existing number for this year
                existing_requests = CertificateRequest.objects.filter(
                    request_id__startswith=f"REQ-{year}-"
                ).order_by('-request_id').first()
                
                if existing_requests:
                    try:
                        last_number = int(existing_requests.request_id.split('-')[-1])
                        next_number = last_number + 1
                    except (ValueError, IndexError):
                        next_number = 1
                else:
                    next_number = 1
                
                # Add some randomness to avoid collisions in concurrent requests
                if attempt > 0:
                    next_number += random.randint(1, 10)
                
                self.request_id = f"REQ-{year}-{next_number:04d}"
                
                # Check if this ID already exists
                if not CertificateRequest.objects.filter(request_id=self.request_id).exists():
                    break
            else:
                # If we couldn't generate a unique ID after max_attempts, use timestamp
                import time
                timestamp = int(time.time() * 1000) % 10000
                self.request_id = f"REQ-{year}-{timestamp:04d}"
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.request_id} - {self.get_certificate_type_display()}"