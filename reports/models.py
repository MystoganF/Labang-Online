from django.db import models
from django.conf import settings

class IncidentReport(models.Model):
    REPORT_TYPES = [
        ('Theft', 'Theft'),
        ('Assault', 'Assault'),
        ('Vandalism', 'Vandalism'),
        ('Disturbance', 'Disturbance'),
        ('Other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Under Investigation', 'Under Investigation'),
        ('Mediation Scheduled', 'Mediation Scheduled'),
        ('Resolved', 'Resolved'),
    ]

    report_id = models.CharField(max_length=20, unique=True, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='incident_reports')
    incident_type = models.CharField(max_length=50, choices=REPORT_TYPES)
    place = models.CharField(max_length=255)
    message = models.TextField()
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status']),
        ]

    def save(self, *args, **kwargs):
        if not self.report_id:
            self.report_id = f"RPT-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.report_id} - {self.incident_type}"
