from django.db import models
from django.conf import settings  # ADD THIS

class Announcement(models.Model):
    ANNOUNCEMENT_TYPES = [
        ('general', 'General Announcement'),
        ('event', 'Event'),
        ('alert', 'Alert'),
        ('maintenance', 'Maintenance'),
    ]
    
    title = models.CharField(max_length=255)
    content = models.TextField()
    announcement_type = models.CharField(max_length=20, choices=ANNOUNCEMENT_TYPES, default='general')
    is_active = models.BooleanField(default=True)
    
    # CHANGE THIS LINE:
    posted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Change from 'User' to 'settings.AUTH_USER_MODEL'
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='announcements'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.created_at.strftime('%Y-%m-%d')}"