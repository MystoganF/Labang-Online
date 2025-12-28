"""
reports/views.py
Handles incident reporting functionality
"""

from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import models

from .models import IncidentReport
from announcements.models import Announcement


@login_required(login_url='accounts:login')
@never_cache
def report_records(request):
    """List all incident reports for the current user"""
    user = request.user
    unread_count = Announcement.objects.filter(is_active=True).count()
    
    # Get all incident reports for the current user
    all_records = IncidentReport.objects.filter(user=user)
    records = all_records.order_by('-created_at')
    
    # Get filter parameters
    query = request.GET.get('q', '').strip()
    status = request.GET.get('status', '').strip()

    # Apply filters
    if query:
        records = records.filter(
            models.Q(report_id__icontains=query) |
            models.Q(incident_type__icontains=query) |
            models.Q(place__icontains=query) |
            models.Q(message__icontains=query)
        )
    
    if status:
        records = records.filter(status=status)

    # Calculate summary statistics
    total_reports = all_records.count()
    pending_count = all_records.filter(status='Pending').count()
    investigation_count = all_records.filter(status='Under Investigation').count()
    resolved_count = all_records.filter(status='Resolved').count()

    context = {
        'user': user,
        'records': records,
        'total_reports': total_reports,
        'pending_count': pending_count,
        'investigation_count': investigation_count,
        'resolved_count': resolved_count,
        'unread_count': unread_count,
    }
    return render(request, 'reports/report_records.html', context)


@login_required(login_url='accounts:login')
@never_cache
def report_detail(request, report_id):
    """View details of a specific incident report"""
    user = request.user
    report = get_object_or_404(IncidentReport, report_id=report_id, user=user)
    unread_count = Announcement.objects.filter(is_active=True).count()
    
    context = {
        'user': user,
        'report': report,
        'unread_count': unread_count,
    }
    return render(request, 'reports/report_detail.html', context)


@login_required(login_url='accounts:login')
@never_cache
def file_report(request):
    """File a new incident report"""
    user = request.user
    unread_count = Announcement.objects.filter(is_active=True).count()
    
    if request.method == 'POST':
        report_type = request.POST.get('report_type')
        place = request.POST.get('place')
        message = request.POST.get('message')
        
        # Validation
        if not report_type or not place or not message:
            messages.error(request, "All fields are required. Please fill in all the information.")
            context = {'user': user}
            return render(request, 'reports/file_report.html', context)
        
        # Validate report type
        valid_report_types = ['Theft', 'Assault', 'Vandalism', 'Disturbance', 'Other']
        if report_type not in valid_report_types:
            messages.error(request, "Invalid report type selected.")
            context = {'user': user}
            return render(request, 'reports/file_report.html', context)
        
        # Validate place (minimum length)
        if len(place.strip()) < 5:
            messages.error(
                request, 
                "Please provide a more detailed location (at least 5 characters)."
            )
            context = {'user': user}
            return render(request, 'reports/file_report.html', context)
        
        # Validate message (minimum length)
        if len(message.strip()) < 20:
            messages.error(
                request, 
                "Please provide a detailed description (at least 20 characters)."
            )
            context = {'user': user}
            return render(request, 'reports/file_report.html', context)
        
        # Create the incident report
        try:
            incident = IncidentReport.objects.create(
                user=user,
                incident_type=report_type,
                place=place.strip(),
                message=message.strip(),
                status='Pending'
            )
            
            return redirect('reports:report_records')
            
        except Exception as e:
            messages.error(request, f"An error occurred while submitting your report: {str(e)}")
            context = {'user': user}
            return render(request, 'reports/file_report.html', context)

    context = {
        'user': user,
        'unread_count': unread_count,
    }
    return render(request, 'reports/file_report.html', context)