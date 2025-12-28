"""
administration/views.py
Handles all admin dashboard and management functionality
"""

from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.cache import never_cache
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q, Count
from django.utils import timezone

from accounts.models import User
from certificates.models import CertificateRequest
from reports.models import IncidentReport
from announcements.models import Announcement


# -------------------- HELPER FUNCTIONS --------------------

def is_admin(user):
    """Check if user is admin"""
    return user.is_staff or user.is_superuser


# -------------------- ADMIN DASHBOARD --------------------

@login_required(login_url='accounts:login')
@user_passes_test(is_admin, login_url='accounts:personal_info')
@never_cache
def admin_dashboard(request):
    """
    Main admin dashboard with summary statistics and recent activities
    """
    
    # Summary Statistics
    total_users = User.objects.filter(is_staff=False).count()
    total_admin = User.objects.filter(is_superuser=True).count()
    verified_users = User.objects.filter(resident_confirmation=True, is_staff=False).count()
    pending_verification = User.objects.filter(resident_confirmation=False, is_staff=False).count()
    
    # Certificate Statistics
    total_certificates = CertificateRequest.objects.count()
    pending_payments = CertificateRequest.objects.filter(payment_status='pending').count()
    paid_certificates = CertificateRequest.objects.filter(payment_status='paid').count()
    unpaid_certificates = CertificateRequest.objects.filter(payment_status='unpaid').count()
    
    # Report Statistics
    total_reports = IncidentReport.objects.count()
    pending_reports = IncidentReport.objects.filter(status='Pending').count()
    under_investigation = IncidentReport.objects.filter(status='Under Investigation').count()
    resolved_reports = IncidentReport.objects.filter(status='Resolved').count()
    
    # Recent Activities
    recent_certificates = CertificateRequest.objects.select_related('user').order_by('-created_at')[:5]
    recent_reports = IncidentReport.objects.select_related('user').order_by('-created_at')[:5]
    recent_users = User.objects.filter(is_staff=False).order_by('-date_joined')[:5]
    
    context = {
        'user': request.user,
        # User statistics
        'total_users': total_users,
        'total_admin': total_admin,
        'verified_users': verified_users,
        'pending_verification': pending_verification,
        # Certificate statistics
        'total_certificates': total_certificates,
        'pending_payments': pending_payments,
        'paid_certificates': paid_certificates,
        'unpaid_certificates': unpaid_certificates,
        # Report statistics
        'total_reports': total_reports,
        'pending_reports': pending_reports,
        'under_investigation': under_investigation,
        'resolved_reports': resolved_reports,
        # Recent activities
        'recent_certificates': recent_certificates,
        'recent_reports': recent_reports,
        'recent_users': recent_users,
    }
    
    return render(request, 'administration/dashboard.html', context)


# -------------------- USER MANAGEMENT --------------------

@login_required(login_url='accounts:login')
@user_passes_test(is_admin, login_url='accounts:personal_info')
@never_cache
def admin_users(request):
    """User management page for admins"""
    
    # Get filter parameters
    query = request.GET.get('q', '').strip()
    verification_status = request.GET.get('verification_status', '').strip()
    
    # Base queryset - exclude staff users
    users = User.objects.filter(is_staff=False).order_by('-date_joined')
    
    # Apply search filter
    if query:
        users = users.filter(
            Q(username__icontains=query) |
            Q(email__icontains=query) |
            Q(full_name__icontains=query) |
            Q(contact_number__icontains=query)
        )
    
    # Apply verification filter
    if verification_status == 'verified':
        users = users.filter(resident_confirmation=True)
    elif verification_status == 'pending':
        users = users.filter(resident_confirmation=False)
    
    context = {
        'user': request.user,
        'users': users,
        'total_users': users.count(),
    }
    
    return render(request, 'administration/users.html', context)


@login_required(login_url='accounts:login')
@user_passes_test(is_admin, login_url='accounts:personal_info')
@never_cache
def admin_verify_user(request, user_id):
    """Verify a user's account"""
    if request.method == 'POST':
        target_user = get_object_or_404(User, id=user_id, is_staff=False)
        target_user.resident_confirmation = True
        target_user.save()
        
        messages.success(request, f"User {target_user.username} has been verified successfully.")
        return redirect('administration:admin_users')
    
    return redirect('administration:admin_users')


@login_required(login_url='accounts:login')
@user_passes_test(is_admin, login_url='accounts:personal_info')
@never_cache
def admin_deactivate_user(request, user_id):
    """Deactivate a user's account"""
    if request.method == 'POST':
        target_user = get_object_or_404(User, id=user_id, is_staff=False)
        target_user.is_active = False
        target_user.save()
        
        messages.success(request, f"User {target_user.username} has been deactivated.")
        return redirect('administration:admin_users')
    
    return redirect('administration:admin_users')


@login_required(login_url='accounts:login')
@user_passes_test(is_admin, login_url='accounts:personal_info')
@never_cache
def admin_activate_user(request, user_id):
    """Activate a user's account"""
    if request.method == 'POST':
        target_user = get_object_or_404(User, id=user_id, is_staff=False)
        target_user.is_active = True
        target_user.save()
        
        messages.success(request, f"User {target_user.username} has been activated.")
        return redirect('administration:admin_users')
    
    return redirect('administration:admin_users')


@login_required(login_url='accounts:login')
@never_cache
def admin_change_user_type(request):
    """
    Change a user's type between Resident and Admin.
    - 'resident' → user.is_superuser = False
    - 'admin'    → user.is_superuser = True
    """
    if not is_admin(request.user):
        messages.error(request, "You do not have permission to perform this action.")
        return redirect('accounts:personal_info')
    
    if request.method != 'POST':
        return redirect('administration:admin_users')

    user_id = request.POST.get('user_id')
    if not user_id:
        messages.error(request, "User ID is required.")
        return redirect('administration:admin_users')

    try:
        target_user = get_object_or_404(User, id=int(user_id))
    except (ValueError, TypeError):
        messages.error(request, "Invalid user ID.")
        return redirect('administration:admin_users')

    new_type = request.POST.get('user_type')
    if new_type not in ['resident', 'admin']:
        messages.error(request, "Invalid user type.")
        return redirect('administration:admin_users')

    # Safety check: don't allow demoting the last admin
    if new_type == 'resident' and target_user.is_superuser:
        remaining_admins = User.objects.filter(is_superuser=True).exclude(pk=target_user.pk)
        if not remaining_admins.exists():
            messages.error(request, "You cannot remove the last admin from admin role.")
            return redirect('administration:admin_users')

    if new_type == 'admin':
        target_user.is_superuser = True
        target_user.is_staff = False
        role_label = "Admin"
    else:  # resident
        target_user.is_superuser = False
        target_user.is_staff = False
        role_label = "Resident"

    target_user.save()

    # If the current admin changed their own role to Resident
    if target_user == request.user and not target_user.is_superuser:
        messages.success(
            request,
            "Your account has been changed to Resident. You will no longer have access to the admin dashboard."
        )
        return redirect('accounts:personal_info')

    messages.success(request, f"User {target_user.username} is now set as {role_label}.")
    return redirect('administration:admin_users')


# -------------------- CERTIFICATE MANAGEMENT --------------------

@login_required(login_url='accounts:login')
@user_passes_test(is_admin, login_url='accounts:personal_info')
@never_cache
def admin_certificates(request):
    """Certificate request management page for admins"""
    
    # Get filter parameters
    query = request.GET.get('q', '').strip()
    certificate_type = request.GET.get('certificate_type', '').strip()
    payment_status = request.GET.get('payment_status', '').strip()
    claim_status = request.GET.get('claim_status', '').strip()
    
    # Base queryset
    certificates = CertificateRequest.objects.select_related('user').order_by('-created_at')
    
    # Apply search filter
    if query:
        certificates = certificates.filter(
            Q(request_id__icontains=query) |
            Q(user__username__icontains=query) |
            Q(user__full_name__icontains=query) |
            Q(purpose__icontains=query)
        )
    
    # Apply filters
    if certificate_type:
        certificates = certificates.filter(certificate_type=certificate_type)
    
    if payment_status:
        certificates = certificates.filter(payment_status=payment_status)
    
    if claim_status:
        certificates = certificates.filter(claim_status=claim_status)
    
    context = {
        'user': request.user,
        'certificates': certificates,
        'total_certificates': certificates.count(),
    }
    
    return render(request, 'administration/certificates.html', context)


@login_required(login_url='accounts:login')
@user_passes_test(is_admin, login_url='accounts:personal_info')
@never_cache
def admin_certificate_detail(request, request_id):
    """
    Certificate detail view (deprecated - using modal instead)
    """
    messages.info(request, "Open certificate details via the View button on the Certificates page.")
    return redirect('administration:admin_certificates')


@login_required(login_url='accounts:login')
@user_passes_test(is_admin, login_url='accounts:personal_info')
@never_cache
def admin_verify_payment(request, request_id):
    """Verify payment for a certificate request"""
    if request.method == 'POST':
        certificate = get_object_or_404(CertificateRequest, request_id=request_id)
        
        if certificate.payment_status == 'pending':
            certificate.payment_status = 'paid'
            certificate.paid_at = timezone.now()
            certificate.save()
            
            messages.success(request, f"Payment verified for request {request_id}.")
        else:
            messages.error(request, "Only pending payments can be verified.")
        
        return redirect('administration:admin_certificates')
    
    return redirect('administration:admin_certificates')


@login_required(login_url='accounts:login')
@user_passes_test(is_admin, login_url='accounts:personal_info')
@never_cache
def admin_reject_payment(request, request_id):
    """Reject payment verification for a certificate request"""
    if request.method == 'POST':
        certificate = get_object_or_404(CertificateRequest, request_id=request_id)
        
        if certificate.payment_status == 'pending':
            certificate.payment_status = 'failed'
            certificate.claim_status = 'failed'
            certificate.save()
            
            messages.success(request, f"Payment rejected for request {request_id}.")
        else:
            messages.error(request, "Only pending payments can be rejected.")
        
        return redirect('administration:admin_certificates')
    
    return redirect('administration:admin_certificates')


@login_required(login_url='accounts:login')
@user_passes_test(is_admin, login_url='accounts:personal_info')
@never_cache
def admin_update_claim_status(request, request_id):
    """Update claim status for a certificate request"""
    if request.method == 'POST':
        certificate = get_object_or_404(CertificateRequest, request_id=request_id)
        new_status = request.POST.get('claim_status')
        
        if new_status in ['processing', 'ready', 'claimed']:
            certificate.claim_status = new_status
            
            if new_status == 'claimed':
                certificate.claimed_at = timezone.now()
            
            certificate.save()
            messages.success(
                request, 
                f"Claim status updated to '{certificate.get_claim_status_display()}' for request {request_id}."
            )
        else:
            messages.error(request, "Invalid claim status.")
        
        return redirect('administration:admin_certificates')
    
    return redirect('administration:admin_certificates')


@login_required(login_url='accounts:login')
@user_passes_test(is_admin, login_url='accounts:personal_info')
@never_cache
def admin_delete_certificate(request, request_id):
    """Delete a certificate request permanently"""
    if request.method == 'POST':
        certificate = get_object_or_404(CertificateRequest, request_id=request_id)
        certificate.delete()
        messages.success(request, f"Certificate request {request_id} has been deleted.")
        return redirect('administration:admin_certificates')
    
    return redirect('administration:admin_certificates')


# -------------------- REPORT MANAGEMENT --------------------

@login_required(login_url='accounts:login')
@user_passes_test(is_admin, login_url='accounts:personal_info')
@never_cache
def admin_reports(request):
    """Incident report management page for admins"""
    
    # Get filter parameters
    query = request.GET.get('q', '').strip()
    incident_type = request.GET.get('incident_type', '').strip()
    status = request.GET.get('status', '').strip()
    
    # Base queryset
    reports = IncidentReport.objects.select_related('user').order_by('-created_at')
    
    # Apply search filter
    if query:
        reports = reports.filter(
            Q(report_id__icontains=query) |
            Q(user__username__icontains=query) |
            Q(user__full_name__icontains=query) |
            Q(place__icontains=query) |
            Q(message__icontains=query)
        )
    
    # Apply filters
    if incident_type:
        reports = reports.filter(incident_type=incident_type)
    
    if status:
        reports = reports.filter(status=status)
    
    context = {
        'user': request.user,
        'reports': reports,
        'total_reports': reports.count(),
    }
    
    return render(request, 'administration/reports.html', context)


@login_required(login_url='accounts:login')
@user_passes_test(is_admin, login_url='accounts:personal_info')
@never_cache
def admin_report_detail(request, report_id):
    """View and manage individual incident report"""
    report = get_object_or_404(IncidentReport, report_id=report_id)
    
    context = {
        'user': request.user,
        'report': report,
    }
    
    return render(request, 'administration/report_detail.html', context)


@login_required(login_url='accounts:login')
@user_passes_test(is_admin, login_url='accounts:personal_info')
@never_cache
def admin_update_report_status(request, report_id):
    """Update status for an incident report"""
    if request.method == 'POST':
        report = get_object_or_404(IncidentReport, report_id=report_id)
        new_status = request.POST.get('status')
        
        valid_statuses = ['Pending', 'Under Investigation', 'Mediation Scheduled', 'Resolved']
        
        if new_status in valid_statuses:
            report.status = new_status
            report.save()
            messages.success(request, f"Report status updated to '{new_status}' for {report_id}.")
        else:
            messages.error(request, "Invalid status.")
        
        return redirect('administration:admin_reports')
    
    return redirect('administration:admin_reports')


@login_required(login_url='accounts:login')
@user_passes_test(is_admin, login_url='accounts:personal_info')
@never_cache
def admin_delete_report(request, report_id):
    """Delete an incident report"""
    if request.method == 'POST':
        report = get_object_or_404(IncidentReport, report_id=report_id)
        report_id_display = report.report_id
        report.delete()
        
        messages.success(request, f"Report {report_id_display} has been deleted.")
        return redirect('administration:admin_reports')
    
    return redirect('administration:admin_reports')


# -------------------- ANNOUNCEMENT MANAGEMENT --------------------

@login_required(login_url='accounts:login')
@user_passes_test(is_admin, login_url='accounts:personal_info')
@never_cache
def admin_announcements(request):
    """Admin view for managing announcements"""
    
    # Get filter parameters
    query = request.GET.get('q', '').strip()
    announcement_type = request.GET.get('type', '').strip()
    status = request.GET.get('status', '').strip()
    
    # Base queryset
    announcements_list = Announcement.objects.select_related('posted_by').order_by('-created_at')
    
    # Apply search filter
    if query:
        announcements_list = announcements_list.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query)
        )
    
    # Apply type filter
    if announcement_type:
        announcements_list = announcements_list.filter(announcement_type=announcement_type)
    
    # Apply status filter
    if status == 'active':
        announcements_list = announcements_list.filter(is_active=True)
    elif status == 'inactive':
        announcements_list = announcements_list.filter(is_active=False)
    
    context = {
        'user': request.user,
        'announcements': announcements_list,
        'total_announcements': announcements_list.count(),
    }
    
    return render(request, 'administration/announcements.html', context)


@login_required(login_url='accounts:login')
@user_passes_test(is_admin, login_url='accounts:personal_info')
@never_cache
def admin_create_announcement(request):
    """Create new announcement"""
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        announcement_type = request.POST.get('announcement_type')
        is_active = request.POST.get('is_active') == 'on'
        
        # Validation
        if not title or not content:
            messages.error(request, "Title and content are required.")
            return redirect('administration:admin_announcements')
        
        if announcement_type not in ['general', 'event', 'alert', 'maintenance']:
            messages.error(request, "Invalid announcement type.")
            return redirect('administration:admin_announcements')
        
        # Create announcement
        Announcement.objects.create(
            title=title,
            content=content,
            announcement_type=announcement_type,
            is_active=is_active,
            posted_by=request.user
        )
        
        messages.success(request, "Announcement created successfully!")
        return redirect('administration:admin_announcements')
    
    return redirect('administration:admin_announcements')


@login_required(login_url='accounts:login')
@user_passes_test(is_admin, login_url='accounts:personal_info')
@never_cache
def admin_edit_announcement(request, announcement_id):
    """Edit existing announcement"""
    announcement = get_object_or_404(Announcement, id=announcement_id)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        announcement_type = request.POST.get('announcement_type')
        is_active = request.POST.get('is_active') == 'on'
        
        # Validation
        if not title or not content:
            messages.error(request, "Title and content are required.")
            return redirect('administration:admin_announcements')
        
        # Update announcement
        announcement.title = title
        announcement.content = content
        announcement.announcement_type = announcement_type
        announcement.is_active = is_active
        announcement.save()
        
        messages.success(request, "Announcement updated successfully!")
        return redirect('administration:admin_announcements')
    
    return redirect('administration:admin_announcements')


@login_required(login_url='accounts:login')
@user_passes_test(is_admin, login_url='accounts:personal_info')
@never_cache
def admin_delete_announcement(request, announcement_id):
    """Delete announcement"""
    if request.method == 'POST':
        announcement = get_object_or_404(Announcement, id=announcement_id)
        announcement.delete()
        
        messages.success(request, "Announcement deleted successfully!")
        return redirect('administration:admin_announcements')
    
    return redirect('administration:admin_announcements')


@login_required(login_url='accounts:login')
@user_passes_test(is_admin, login_url='accounts:personal_info')
@never_cache
def admin_toggle_announcement(request, announcement_id):
    """Toggle announcement active status"""
    if request.method == 'POST':
        announcement = get_object_or_404(Announcement, id=announcement_id)
        announcement.is_active = not announcement.is_active
        announcement.save()
        
        status = "activated" if announcement.is_active else "deactivated"
        messages.success(request, f"Announcement {status} successfully!")
        return redirect('administration:admin_announcements')
    
    return redirect('administration:admin_announcements')