"""
certificates/views.py
Handles certificate requests and payment processing
"""

from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from .models import CertificateRequest
from announcements.models import Announcement


# -------------------- CERTIFICATE REQUEST VIEWS --------------------

@login_required(login_url='accounts:login')
@never_cache
def document_request(request):
    """Main document request page showing available certificates"""
    user = request.user
    unread_count = Announcement.objects.filter(is_active=True).count()
    
    context = {
        'user': user,
        'unread_count': unread_count,
        'active_page': 'document_request',  # This highlights the menu item
    }
    return render(request, 'certificates/document_request.html', context)


@login_required(login_url='accounts:login')
@never_cache
def certificate_requests(request):
    """List all certificate requests for the current user"""
    user = request.user
    unread_count = Announcement.objects.filter(is_active=True).count()

    # Get filter parameters
    certificate_type = request.GET.get('certificate_type', '').strip()
    payment_status = request.GET.get('payment_status', '').strip()
    claim_status = request.GET.get('claim_status', '').strip()
    payment_mode = request.GET.get('payment_mode', '').strip()
    
    # Base queryset
    requests = CertificateRequest.objects.filter(user=user)
    
    # Apply filters
    valid_cert_types = ['barangay_clearance', 'residency', 'indigency', 'good_moral', 'business_clearance']
    if certificate_type and certificate_type in valid_cert_types:
        requests = requests.filter(certificate_type=certificate_type)
    
    valid_payment_statuses = ['unpaid', 'pending', 'paid', 'failed']
    if payment_status and payment_status in valid_payment_statuses:
        requests = requests.filter(payment_status=payment_status)
    
    valid_claim_statuses = ['processing', 'ready', 'claimed', 'failed']
    if claim_status and claim_status in valid_claim_statuses:
        requests = requests.filter(claim_status=claim_status)
    
    valid_payment_modes = ['gcash', 'counter']
    if payment_mode and payment_mode in valid_payment_modes:
        requests = requests.filter(payment_mode=payment_mode)
    
    # Order by most recent first
    requests = requests.order_by('-created_at')
    
    # Calculate summary statistics
    all_requests = CertificateRequest.objects.filter(user=user)
    total_requests = all_requests.count()
    pending_count = all_requests.filter(payment_status='pending').count()
    paid_count = all_requests.filter(payment_status='paid').count()
    unpaid_count = all_requests.filter(payment_status='unpaid').count()
    
    context = {
        'user': user,
        'requests': requests,
        'total_requests': total_requests,
        'pending_count': pending_count,
        'paid_count': paid_count,
        'unpaid_count': unpaid_count,
        'unread_count': unread_count,
        'active_page': 'document_request',
    }
    return render(request, 'certificates/certificate_requests.html', context)


@login_required(login_url='accounts:login')
@never_cache
def request_detail(request, request_id):
    """View details of a specific certificate request"""
    user = request.user
    unread_count = Announcement.objects.filter(is_active=True).count()

    cert_request = get_object_or_404(CertificateRequest, request_id=request_id, user=user)
    
    # Determine recommended action
    next_action = None
    if cert_request.payment_status == 'unpaid':
        if not cert_request.payment_mode:
            next_action = {
                'label': 'Select Payment Mode',
                'url_name': 'certificates:payment_mode_selection',
            }
        elif cert_request.payment_mode == 'gcash':
            next_action = {
                'label': 'Proceed to GCash Payment',
                'url_name': 'certificates:gcash_payment',
            }
        elif cert_request.payment_mode == 'counter':
            next_action = {
                'label': 'Proceed to Counter Payment',
                'url_name': 'certificates:counter_payment',
            }

    context = {
        'user': user,
        'cert_request': cert_request,
        'next_action': next_action,
        'unread_count': unread_count,
        'active_page': 'document_request',
    }
    return render(request, 'certificates/request_detail.html', context)


# -------------------- CERTIFICATE TYPE FORMS --------------------

@login_required(login_url='accounts:login')
@never_cache
def barangay_clearance_request(request):
    """Request form for Barangay Clearance"""
    user = request.user
    unread_count = Announcement.objects.filter(is_active=True).count()
    
    if request.method == 'POST':
        purpose = request.POST.get('purpose')
        
        if not purpose or len(purpose.strip()) < 10:
            messages.error(
                request, 
                "Please provide a detailed purpose for your request (at least 10 characters)."
            )
            context = {'user': user, 'active_page': 'document_request',}
            return render(request, 'certificates/barangay_clearance_request.html', context)
        
        cert_request = CertificateRequest.objects.create(
            user=user,
            certificate_type='barangay_clearance',
            purpose=purpose,
            payment_amount=50.00,
        )
        
        messages.success(
            request, 
            f"Request submitted successfully! Your request ID is {cert_request.request_id}. Please proceed to payment."
        )
        
        return redirect('certificates:payment_mode_selection', request_id=cert_request.request_id)
    
    context = {
        'user': user,
        'unread_count': unread_count,
        'active_page': 'document_request',
    }
    return render(request, 'certificates/barangay_clearance_request.html', context)


@login_required(login_url='accounts:login')
@never_cache
def brgy_residency_cert(request):
    """Request form for Certificate of Residency"""
    user = request.user
    unread_count = Announcement.objects.filter(is_active=True).count()
    
    if request.method == 'POST':
        purpose = request.POST.get('purpose')
        
        if not purpose or len(purpose.strip()) < 10:
            messages.error(
                request, 
                "Please provide a detailed purpose for your request (at least 10 characters)."
            )
            context = {'user': user, 'active_page': 'document_request',}
            return render(request, 'certificates/brgy_residency_cert.html', context)
        
        cert_request = CertificateRequest.objects.create(
            user=user,
            certificate_type='residency',
            purpose=purpose,
            payment_amount=30.00,
        )
        
        messages.success(
            request, 
            f"Request submitted successfully! Your request ID is {cert_request.request_id}. Please proceed to payment."
        )
        
        return redirect('certificates:payment_mode_selection', request_id=cert_request.request_id)
    
    context = {
        'user': user,
        'unread_count': unread_count,
        'active_page': 'document_request',
    }
    return render(request, 'certificates/brgy_residency_cert.html', context)


@login_required(login_url='accounts:login')
@never_cache
def brgy_indigency_cert(request):
    """Request form for Certificate of Indigency"""
    user = request.user
    unread_count = Announcement.objects.filter(is_active=True).count()
    
    if request.method == 'POST':
        purpose = request.POST.get('purpose')
        proof_photo = request.FILES.get('proof_photo')
        
        if not purpose or len(purpose.strip()) < 10:
            messages.error(
                request, 
                "Please provide a detailed purpose for your request (at least 10 characters)."
            )
            context = {'user': user, 'active_page': 'document_request',}
            return render(request, 'certificates/brgy_indigency_cert.html', context)
        
        if not proof_photo:
            messages.error(
                request, 
                "Please upload a proof photo for your indigency certificate request."
            )
            context = {'user': user, 'active_page': 'document_request',}
            return render(request, 'certificates/brgy_indigency_cert.html', context)

        # Validate image type and size
        allowed_types = {'image/jpeg', 'image/jpg', 'image/png'}
        if getattr(proof_photo, 'content_type', '').lower() not in allowed_types:
            messages.error(request, "Invalid image type. Please upload a JPG or PNG file.")
            context = {'user': user}
            return render(request, 'certificates/brgy_indigency_cert.html', context)

        max_size_mb = 5
        if hasattr(proof_photo, 'size') and proof_photo.size > max_size_mb * 1024 * 1024:
            messages.error(request, f"Image too large. Please upload a file under {max_size_mb} MB.")
            context = {'user': user, 'active_page': 'document_request',}
            return render(request, 'certificates/brgy_indigency_cert.html', context)

        # Upload proof photo
        from accounts.storage_utils import upload_to_supabase
        proof_photo_url = upload_to_supabase(
            proof_photo, 
            bucket_name='user-uploads',
            folder='indigency-proofs'
        )

        if not proof_photo_url:
            messages.error(request, "Failed to upload proof photo. Please try again later.")
            context = {'user': user, 'active_page': 'document_request',}
            return render(request, 'certificates/brgy_indigency_cert.html', context)
        
        cert_request = CertificateRequest.objects.create(
            user=user,
            certificate_type='indigency',
            purpose=purpose,
            proof_photo_url=proof_photo_url,
            payment_amount=30.00,
        )
        
        messages.success(
            request, 
            f"Request submitted successfully! Your request ID is {cert_request.request_id}. Please proceed to payment."
        )
        
        return redirect('certificates:payment_mode_selection', request_id=cert_request.request_id)
    
    context = {
        'user': user,
        'unread_count': unread_count,
        'active_page': 'document_request',
    }
    return render(request, 'certificates/brgy_indigency_cert.html', context)


@login_required(login_url='accounts:login')
@never_cache
def brgy_goodmoral_character(request):
    """Request form for Good Moral Character Certificate"""
    user = request.user
    unread_count = Announcement.objects.filter(is_active=True).count()
    
    if request.method == 'POST':
        purpose = request.POST.get('purpose')
        
        if not purpose or len(purpose.strip()) < 10:
            messages.error(
                request, 
                "Please provide a detailed purpose for your request (at least 10 characters)."
            )
            context = {'user': user, 'active_page': 'document_request',}
            return render(request, 'certificates/brgy_goodmoral_character.html', context)
        
        cert_request = CertificateRequest.objects.create(
            user=user,
            certificate_type='good_moral',
            purpose=purpose,
            payment_amount=40.00,
        )
        
        messages.success(
            request, 
            f"Request submitted successfully! Your request ID is {cert_request.request_id}. Please proceed to payment."
        )
        
        return redirect('certificates:payment_mode_selection', request_id=cert_request.request_id)
    
    context = {
        'user': user,
        'unread_count': unread_count,
        'active_page': 'document_request',
    }
    return render(request, 'certificates/brgy_goodmoral_character.html', context)


@login_required(login_url='accounts:login')
@never_cache
def brgy_business_cert(request):
    """Request form for Business Clearance"""
    user = request.user
    unread_count = Announcement.objects.filter(is_active=True).count()
    
    if request.method == 'POST':
        purpose = request.POST.get('purpose')
        business_name = request.POST.get('business_name')
        business_type = request.POST.get('business_type')
        business_nature = request.POST.get('business_nature')
        business_address = request.POST.get('business_address')
        employees_count = request.POST.get('employees_count')
        
        if not purpose or len(purpose.strip()) < 10:
            messages.error(
                request, 
                "Please provide a detailed purpose for your request (at least 10 characters)."
            )
            context = {'user': user, 'active_page': 'document_request',}
            return render(request, 'certificates/brgy_business_cert.html', context)
        
        if not all([business_name, business_type, business_nature, business_address, employees_count]):
            messages.error(request, "Please fill in all required business information fields.")
            context = {'user': user, 'active_page': 'document_request',}
            return render(request, 'certificates/brgy_business_cert.html', context)
        
        try:
            employees_count = int(employees_count)
            if employees_count < 0:
                raise ValueError("Number of employees cannot be negative")
        except ValueError:
            messages.error(request, "Please enter a valid number of employees.")
            context = {'user': user, 'active_page': 'document_request',}
            return render(request, 'certificates/brgy_business_cert.html', context)
        
        cert_request = CertificateRequest.objects.create(
            user=user,
            certificate_type='business_clearance',
            purpose=purpose,
            business_name=business_name,
            business_type=business_type,
            business_nature=business_nature,
            business_address=business_address,
            employees_count=employees_count,
            payment_amount=100.00,
        )
        
        messages.success(
            request, 
            f"Request submitted successfully! Your request ID is {cert_request.request_id}. Please proceed to payment."
        )
        
        return redirect('certificates:payment_mode_selection', request_id=cert_request.request_id)
    
    context = {
        'user': user,
        'unread_count': unread_count,
        'active_page': 'document_request',
    }
    return render(request, 'certificates/brgy_business_cert.html', context)


# -------------------- PAYMENT VIEWS --------------------

@login_required(login_url='accounts:login')
@never_cache
def payment_mode_selection(request, request_id):
    """Select payment mode (GCash or Counter)"""
    user = request.user
    unread_count = Announcement.objects.filter(is_active=True).count()
    
    cert_request = get_object_or_404(CertificateRequest, request_id=request_id, user=user)
    
    if cert_request.payment_status == 'paid':
        messages.info(request, "This request has already been paid.")
        return redirect('certificates:certificate_requests')
    
    if request.method == 'POST':
        payment_mode = request.POST.get('payment_mode')
        
        if payment_mode not in ['gcash', 'counter']:
            messages.error(request, "Invalid payment mode selected.")
            context = {
                'user': user,
                'cert_request': cert_request,
                'active_page': 'document_request',
            }
            return render(request, 'certificates/payment_mode_selection.html', context)
        
        cert_request.payment_mode = payment_mode
        cert_request.save()
        
        if payment_mode == 'gcash':
            return redirect('certificates:gcash_payment', request_id=cert_request.request_id)
        else:
            return redirect('certificates:counter_payment', request_id=cert_request.request_id)
    
    context = {
        'user': user,
        'cert_request': cert_request,
        'unread_count': unread_count,
        'active_page': 'document_request',
    }
    return render(request, 'certificates/payment_mode_selection.html', context)


@login_required(login_url='accounts:login')
@never_cache
def gcash_payment(request, request_id):
    """GCash payment submission"""
    user = request.user
    unread_count = Announcement.objects.filter(is_active=True).count()
    
    cert_request = get_object_or_404(CertificateRequest, request_id=request_id, user=user)
    
    if cert_request.payment_status == 'paid':
        messages.info(request, "This request has already been paid.")
        return redirect('certificates:certificate_requests')
    
    if cert_request.payment_mode != 'gcash':
        messages.error(request, "Invalid payment mode for this request.")
        return redirect('certificates:payment_mode_selection', request_id=request_id)
    
    if request.method == 'POST':
        reference_number = request.POST.get('reference_number', '').strip()
        
        if not reference_number:
            messages.error(request, "Please enter your GCash reference number.")
            context = {
                'user': user,
                'cert_request': cert_request,
                'active_page': 'document_request',
            }
            return render(request, 'certificates/gcash_payment.html', context)
        
        if len(reference_number) < 10:
            messages.error(request, "Invalid reference number. Please check and try again.")
            context = {
                'user': user,
                'cert_request': cert_request,
                'active_page': 'document_request',
            }
            return render(request, 'certificates/gcash_payment.html', context)
        
        cert_request.payment_reference = reference_number
        cert_request.payment_status = 'pending'
        cert_request.save()
        
        messages.success(
            request, 
            f"Payment reference submitted successfully! Your reference number {reference_number} "
            "is now pending verification by our staff. You will be notified once verified."
        )
        
        return redirect('certificates:certificate_requests')
    
    context = {
        'user': user,
        'cert_request': cert_request,
        'unread_count': unread_count,
        'active_page': 'document_request',
    }
    return render(request, 'certificates/gcash_payment.html', context)


@login_required(login_url='accounts:login')
@never_cache
def counter_payment(request, request_id):
    """Counter payment (pay on-site)"""
    user = request.user
    unread_count = Announcement.objects.filter(is_active=True).count()

    cert_request = get_object_or_404(CertificateRequest, request_id=request_id, user=user)

    if cert_request.payment_status == 'paid':
        messages.info(request, "This request has already been paid.")
        return redirect('certificates:certificate_requests')

    if cert_request.payment_mode != 'counter':
        cert_request.payment_mode = 'counter'
        cert_request.save(update_fields=['payment_mode'])

    if request.method == 'POST':
        cert_request.payment_status = 'pending'
        cert_request.payment_reference = f"COUNTER-{cert_request.request_id}"
        cert_request.save(update_fields=['payment_status', 'payment_reference'])
        return redirect('certificates:certificate_requests')

    context = {
        'user': user,
        'cert_request': cert_request,
        'unread_count': unread_count,
        'active_page': 'document_request',
    }
    return render(request, 'certificates/counter_payment.html', context)


@login_required(login_url='accounts:login')
@never_cache
def cancel_request(request, request_id):
    """Cancel an unpaid certificate request"""
    user = request.user
    cert_request = get_object_or_404(CertificateRequest, request_id=request_id, user=user)
    
    if cert_request.payment_status != 'unpaid':
        messages.error(
            request, 
            "Only unpaid requests can be cancelled. Paid requests cannot be cancelled as we do not offer refunds."
        )
        return redirect('certificates:certificate_requests')
    
    request_id_display = cert_request.request_id
    cert_request.delete()
    
    return redirect('certificates:certificate_requests')