"""
announcements/views.py
Handles announcement viewing for users
"""

from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.shortcuts import render

from .models import Announcement


@login_required(login_url='accounts:login')
@never_cache
def announcements(request):
    """
    User view for announcements
    Displays all active announcements to users
    """
    user = request.user
    
    # Get only active announcements
    announcements_list = Announcement.objects.filter(is_active=True).select_related('posted_by')
    
    # Get filter parameters
    announcement_type = request.GET.get('type', '').strip()
    
    # Apply type filter if provided
    if announcement_type and announcement_type in ['general', 'event', 'alert', 'maintenance']:
        announcements_list = announcements_list.filter(announcement_type=announcement_type)
    
    # Count unread (for badge)
    unread_count = announcements_list.count()
    
    context = {
        'user': user,
        'announcements': announcements_list,
        'unread_count': unread_count,
        'active_page': 'announcements',
        
    }
    
    return render(request, 'announcements/announcements.html', context)