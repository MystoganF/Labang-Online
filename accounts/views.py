# views.py
"""
Views for Labang Online application
Handles authentication, user management, and password recovery
"""



from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache

from django.shortcuts import render
from .models import User, PasswordResetCode
from .forms import RegistrationForm
from .models import User, PasswordResetCode, CertificateRequest, IncidentReport, Announcement
from django.db import models  # Add this for Q queries


from django.db.models import Q, Count
from django.http import JsonResponse
from django.contrib.auth.decorators import user_passes_test

import google.generativeai as genai
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import json
import os




# -------------------- LOGIN --------------------
# unread_count = Announcement.objects.filter(is_active=True).count()
# unread_count = 1

@never_cache
def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.resident_confirmation:  # Only allow verified users
                auth_login(request, user)
                return redirect('accounts:personal_info')
            else:
                messages.warning(request, "Account verification pending. Please visit Barangay Hall of Labangon to complete your account verification.")
        else:
            messages.error(request, "Invalid credentials. Please check your username and password and try again.")

    return render(request, 'accounts/login.html')


# -------------------- REGISTER --------------------
@never_cache
def register(request):
    if request.method == "POST":
        # Get form data
        full_name = request.POST.get("full_name")
        username = request.POST.get("username")
        email = request.POST.get("email")
        contact_number = request.POST.get("contact_number")
        date_of_birth = request.POST.get("date_of_birth")
        address_line = request.POST.get("address_line")
        barangay = request.POST.get("barangay", "Labangon")
        city = request.POST.get("city", "Cebu City")
        province = request.POST.get("province", "Cebu")
        postal_code = request.POST.get("postal_code", "6000")
        password = request.POST.get("password")
        resident_confirmation = request.POST.get("resident_confirmation") == "on"
      

        # Check if email or username already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, "This email address is already registered. Please use a different email or log in to your existing account.")
            return render(request, "accounts/register.html")
        if User.objects.filter(username=username).exists():
            messages.error(request, "This username is already taken. Please choose a different username.")
            return render(request, "accounts/register.html")

        # Create the user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            full_name=full_name,
            contact_number=contact_number,
            date_of_birth=date_of_birth,
            address_line=address_line,
            barangay=barangay,
            city=city,
            province=province,
            postal_code=postal_code,
            resident_confirmation=resident_confirmation,
            
        )

        messages.success(request, "Account created successfully! Please proceed to Barangay Hall of Labangon for verification.")
        return redirect("accounts:login")

    return render(request, "accounts/register.html")


# -------------------- WELCOME PAGE --------------------
def welcome(request: HttpRequest) -> HttpResponse:
    return render(request, 'accounts/welcome.html')


# -------------------- PUBLIC HOME / LANDING --------------------
def home(request: HttpRequest) -> HttpResponse:
    """Public landing page with sections, always accessible.
    Uses base header with Login/Register links.
    """
    return render(request, 'home.html')


# -------------------- FORGOT PASSWORD --------------------
def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        
        try:
            user = User.objects.get(email=email)
            
            # Generate verification code
            reset_code = PasswordResetCode.generate_code(user)
            
            # Send email with verification code
            subject = 'Password Reset Verification Code - Labang Online'
            message = f"""
            Hello {user.full_name},
            
            You requested a password reset for your Labang Online account.
            
            Your verification code is: {reset_code.code}
            
            This code will expire in 5 minutes.
            
            If you didn't request this password reset, please ignore this email.
            
            Best regards,
            Labang Online Team
            """
            
            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                )
                messages.success(request, f"Verification code sent to {email}. Please check your email and enter the 6-digit code.")
                return redirect('accounts:verify_code', user_id=user.id)
            except Exception as e:
                messages.error(request, f"Failed to send email. Please try again later. Error: {str(e)}")
                
        except User.DoesNotExist:
            # Don't reveal if email exists or not for security
            messages.success(request, f"If an account exists with {email}, a verification code has been sent.")
            return redirect('accounts:login')
    
    return render(request, 'accounts/forgot_password.html')


# -------------------- VERIFY CODE --------------------
def verify_code(request, user_id):
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        entered_code = request.POST.get('code')
        
        try:
            reset_code = PasswordResetCode.objects.get(
                user=user, 
                code=entered_code, 
                is_used=False
            )
            
            if reset_code.is_valid():
                # Store the code in session for password reset
                request.session['reset_code_id'] = reset_code.id
                messages.success(request, "Code verified successfully! Please enter your new password.")
                return redirect('accounts:reset_password')
            else:
                messages.error(request, "Code has expired. Please request a new code.")
                return redirect('accounts:forgot_password')
                
        except PasswordResetCode.DoesNotExist:
            messages.error(request, "Invalid verification code. Please try again.")
    
    context = {'user': user, 'hide_user_nav': True}
    return render(request, 'accounts/verify_code.html', context)


# -------------------- RESEND VERIFICATION CODE --------------------
def resend_code(request, user_id):
    user = get_object_or_404(User, id=user_id)
    
    # Generate a new code and send email
    reset_code = PasswordResetCode.generate_code(user)
    subject = 'Password Reset Verification Code - Labang Online'
    message = f"""
    Hello {user.full_name},
    
    Here is your new verification code for resetting your password:
    
    Your verification code is: {reset_code.code}
    
    This code will expire in 5 minutes.
    
    If you didn't request this password reset, please ignore this email.
    
    Best regards,
    Labang Online Team
    """
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        messages.success(request, f"A new verification code was sent to {user.email}.")
    except Exception as e:
        messages.error(request, f"Failed to send email. Please try again later. Error: {str(e)}")
    
    # Return to verify page with minimal header
    return redirect('accounts:verify_code', user_id=user.id)


# -------------------- RESET PASSWORD --------------------
def reset_password(request):
    if 'reset_code_id' not in request.session:
        messages.error(request, "No active password reset session. Please start over.")
        return redirect('accounts:forgot_password')
    
    try:
        reset_code = PasswordResetCode.objects.get(
            id=request.session['reset_code_id'],
            is_used=False
        )
        
        if not reset_code.is_valid():
            messages.error(request, "Reset session expired. Please request a new code.")
            del request.session['reset_code_id']
            return redirect('accounts:forgot_password')
            
    except PasswordResetCode.DoesNotExist:
        messages.error(request, "Invalid reset session. Please start over.")
        del request.session['reset_code_id']
        return redirect('accounts:forgot_password')
    
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'accounts/reset_password.html')
        
        if len(new_password) < 8:
            messages.error(request, "Password must be at least 8 characters long.")
            return render(request, 'accounts/reset_password.html')
        
        # Update user password
        reset_code.user.set_password(new_password)
        reset_code.user.save()
        
        # Mark code as used
        reset_code.is_used = True
        reset_code.save()
        
        # Clear session
        del request.session['reset_code_id']
        
        messages.success(request, "Password updated successfully! You can now log in with your new password.")
        return redirect('accounts:login')
    
    return render(request, 'accounts/reset_password.html')


# -------------------- LOGOUT CONFIRM --------------------
@login_required(login_url='accounts:login')
@never_cache
def logout_confirm(request):
    storage = messages.get_messages(request)
    storage.used = True
    
    if request.method == 'POST':
        auth_logout(request)
        messages.success(request, "You have successfully logged out.")
        return redirect('accounts:login')
    return render(request, 'accounts/logout_confirm.html')


# -------------------- PERSONAL INFO --------------------

@login_required(login_url='accounts:login')
@never_cache
def personal_info(request):
    storage = messages.get_messages(request)
    storage.used = True

    user = request.user
    
    # Get unread announcement count
    unread_count = Announcement.objects.filter(is_active=True).count()

    context = {
        'user': user,
        'unread_count': unread_count,
    }   
    return render(request, 'accounts/personal_info.html', context)


# -------------------- EDIT PROFILE --------------------
@login_required(login_url='accounts:login')
@never_cache
def edit_profile(request):
    user = request.user
    
    unread_count = Announcement.objects.filter(is_active=True).count()

    if request.method == 'POST':
        save_ok = True
        # Update text fields
        user.full_name = request.POST.get('full_name', user.full_name)
        user.contact_number = request.POST.get('contact_number', user.contact_number)
        user.address_line = request.POST.get('address_line', user.address_line)
        
        # Handle username with uniqueness check
        new_username = request.POST.get('username')
        if new_username and new_username != user.username:
            if User.objects.filter(username=new_username).exclude(pk=user.pk).exists():
                messages.error(request, "Username already taken. Please choose another.")
                save_ok = False
            else:
                user.username = new_username
        
        # Handle date_of_birth
        date_of_birth = request.POST.get('date_of_birth')
        if date_of_birth:
            user.date_of_birth = date_of_birth
            
        # Handle civil_status
        civil_status = request.POST.get('civil_status')
        if civil_status:
            user.civil_status = civil_status

        # Handle file uploads to Supabase Storage
        from .storage_utils import upload_to_supabase, delete_from_supabase
        
        profile_photo = request.FILES.get('profile_photo')
        if profile_photo:
            # Delete old photo if it exists
            if user.profile_photo_url:
                delete_from_supabase(user.profile_photo_url, bucket_name='user-uploads')
            
            # Upload new photo
            new_url = upload_to_supabase(
                profile_photo, 
                bucket_name='user-uploads',
                folder='profile-photos'
            )
            
            if new_url:
                user.profile_photo_url = new_url
            else:
                messages.error(request, "Failed to upload profile photo. Please try again.")
                save_ok = False

        resident_id_photo = request.FILES.get('resident_id_photo')
        if resident_id_photo:
            # Delete old ID photo if it exists
            if user.resident_id_photo_url:
                delete_from_supabase(user.resident_id_photo_url, bucket_name='user-uploads')
            
            # Upload new ID photo
            new_url = upload_to_supabase(
                resident_id_photo, 
                bucket_name='user-uploads',
                folder='resident-ids'
            )
            
            if new_url:
                user.resident_id_photo_url = new_url
            else:
                messages.error(request, "Failed to upload resident ID photo. Please try again.")
                save_ok = False

        if save_ok:
            user.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('accounts:personal_info')
        else:
            context = {
                'user': user,
            }
            return render(request, 'accounts/edit_profile.html', context)

    context = {
        'user': user,
        'unread_count': unread_count,
    }
    return render(request, 'accounts/edit_profile.html', context)


# -------------------- VIEW COMPLETE PROFILE --------------------
@login_required(login_url='accounts:login')
@never_cache
def complete_profile(request):
    user = request.user
    
    # If you have a Dependent model, fetch dependents here
    dependents = []
    
    context = {
        'user': user,
        'dependents': dependents,
    }
    return render(request, 'accounts/complete_profile.html', context)


@login_required(login_url='accounts:login')
@never_cache
def document_request(request):
    user = request.user
    unread_count = Announcement.objects.filter(is_active=True).count()
    
    context = {
        'user': user,
        'unread_count': unread_count,
    }
    return render(request, 'accounts/document_request.html', context)


@login_required(login_url='accounts:login')
@never_cache
def certificate_requests(request):
    user = request.user
    unread_count = Announcement.objects.filter(is_active=True).count()

    # Get filter parameters - use .get() with empty string default
    certificate_type = request.GET.get('certificate_type', '').strip()
    payment_status = request.GET.get('payment_status', '').strip()
    claim_status = request.GET.get('claim_status', '').strip()
    payment_mode = request.GET.get('payment_mode', '').strip()
    
    # Base queryset - all user's requests ordered by most recent first
    requests = CertificateRequest.objects.filter(user=user)
    
    # Apply filters only if values are provided and valid
    valid_cert_types = ['barangay_clearance', 'residency', 'indigency', 'good_moral', 'business_clearance']
    if certificate_type and certificate_type in valid_cert_types:
        requests = requests.filter(certificate_type=certificate_type)
    
    valid_payment_statuses = ['unpaid', 'pending', 'paid', 'failed']
    if payment_status and payment_status in valid_payment_statuses:
        requests = requests.filter(payment_status=payment_status)
    
    valid_claim_statuses = ['processing', 'ready', 'claimed']
    if claim_status and claim_status in valid_claim_statuses:
        requests = requests.filter(claim_status=claim_status)
    
    valid_payment_modes = ['gcash', 'counter']
    if payment_mode and payment_mode in valid_payment_modes:
        requests = requests.filter(payment_mode=payment_mode)
    
    # Order by most recent first
    requests = requests.order_by('-created_at')
    
    # Calculate summary statistics (always from all user requests, not filtered)
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
        
    }
    return render(request, 'accounts/certificate_requests.html', context)


@login_required(login_url='accounts:login')
@never_cache
def request_detail(request, request_id):
    user = request.user
    unread_count = Announcement.objects.filter(is_active=True).count()

    cert_request = get_object_or_404(CertificateRequest, request_id=request_id, user=user)
    
    # Determine recommended action for convenience
    next_action = None
    if cert_request.payment_status == 'unpaid':
        if not cert_request.payment_mode:
            next_action = {
                'label': 'Select Payment Mode',
                'url_name': 'accounts:payment_mode_selection',
            }
        elif cert_request.payment_mode == 'gcash':
            next_action = {
                'label': 'Proceed to GCash Payment',
                'url_name': 'accounts:gcash_payment',
            }
        elif cert_request.payment_mode == 'counter':
            next_action = {
                'label': 'Proceed to Counter Payment',
                'url_name': 'accounts:counter_payment',
            }

    context = {
        'user': user,
        'cert_request': cert_request,
        'next_action': next_action,
        'unread_count': unread_count,
    }
    return render(request, 'accounts/request_detail.html', context)


@login_required(login_url='accounts:login')
@never_cache
def barangay_clearance_request(request):
    user = request.user
    unread_count = Announcement.objects.filter(is_active=True).count()
    
    if request.method == 'POST':
        purpose = request.POST.get('purpose')
        
        # Validate purpose
        if not purpose or len(purpose.strip()) < 10:
            messages.error(request, "Please provide a detailed purpose for your request (at least 10 characters).")
            context = {
                'user': user,
            }
            return render(request, 'accounts/barangay_clearance_request.html', context)
        
        # Create the certificate request
        cert_request = CertificateRequest.objects.create(
            user=user,
            certificate_type='barangay_clearance',
            purpose=purpose,
            payment_amount=50.00,  # Barangay Clearance fee
        )
        
        messages.success(request, f"Request submitted successfully! Your request ID is {cert_request.request_id}. Please proceed to payment.")
        
        # Redirect to payment mode selection
        return redirect('accounts:payment_mode_selection', request_id=cert_request.request_id)
    
    context = {
        'user': user,
        'unread_count': unread_count,
    }
    return render(request, 'accounts/barangay_clearance_request.html', context)


@login_required(login_url='accounts:login')
@never_cache
def brgy_residency_cert(request):
    user = request.user
    unread_count = Announcement.objects.filter(is_active=True).count()
    
    if request.method == 'POST':
        purpose = request.POST.get('purpose')
        
        # Validate purpose
        if not purpose or len(purpose.strip()) < 10:
            messages.error(request, "Please provide a detailed purpose for your request (at least 10 characters).")
            context = {
                'user': user,
            }
            return render(request, 'accounts/brgy_residency_cert.html', context)
        
        # Create the certificate request
        cert_request = CertificateRequest.objects.create(
            user=user,
            certificate_type='residency',
            purpose=purpose,
            payment_amount=30.00,  # Certificate of Residency fee
        )
        
        messages.success(request, f"Request submitted successfully! Your request ID is {cert_request.request_id}. Please proceed to payment.")
        
        # Redirect to payment mode selection
        return redirect('accounts:payment_mode_selection', request_id=cert_request.request_id)
    
    context = {
        'user': user,
        'unread_count': unread_count,
    }
    return render(request, 'accounts/brgy_residency_cert.html', context)


@login_required(login_url='accounts:login')
@never_cache
def brgy_indigency_cert(request):
    user = request.user
    unread_count = Announcement.objects.filter(is_active=True).count()
    
    if request.method == 'POST':
        purpose = request.POST.get('purpose')
        proof_photo = request.FILES.get('proof_photo')
        
        # Validate purpose and proof photo
        if not purpose or len(purpose.strip()) < 10:
            messages.error(request, "Please provide a detailed purpose for your request (at least 10 characters).")
            context = {
                'user': user,
            }
            return render(request, 'accounts/brgy_indigency_cert.html', context)
        
        if not proof_photo:
            messages.error(request, "Please upload a proof photo for your indigency certificate request.")
            context = {
                'user': user,
            }
            return render(request, 'accounts/brgy_indigency_cert.html', context)
        
        # Upload proof photo to Supabase
        from .storage_utils import upload_to_supabase
        proof_photo_url = upload_to_supabase(
            proof_photo, 
            bucket_name='user-uploads',
            folder='indigency-proofs'
        )
        
        if not proof_photo_url:
            messages.error(request, "Failed to upload proof photo. Please try again.")
            context = {
                'user': user,
            }
            return render(request, 'accounts/brgy_indigency_cert.html', context)
        
        # Create the certificate request
        cert_request = CertificateRequest.objects.create(
            user=user,
            certificate_type='indigency',
            purpose=purpose,
            proof_photo_url=proof_photo_url,
            payment_amount=30.00,  # Certificate of Indigency fee
        )
        
        messages.success(request, f"Request submitted successfully! Your request ID is {cert_request.request_id}. Please proceed to payment.")
        
        # Redirect to payment mode selection
        return redirect('accounts:payment_mode_selection', request_id=cert_request.request_id)
    
    context = {
        'user': user,
        'unread_count': unread_count,
    }
    return render(request, 'accounts/brgy_indigency_cert.html', context)


@login_required(login_url='accounts:login')
@never_cache
def brgy_goodmoral_character(request):
    user = request.user
    unread_count = Announcement.objects.filter(is_active=True).count()
    
    if request.method == 'POST':
        purpose = request.POST.get('purpose')
        
        # Validate purpose
        if not purpose or len(purpose.strip()) < 10:
            messages.error(request, "Please provide a detailed purpose for your request (at least 10 characters).")
            context = {
                'user': user,
            }
            return render(request, 'accounts/brgy_goodmoral_character.html', context)
        
        # Create the certificate request
        cert_request = CertificateRequest.objects.create(
            user=user,
            certificate_type='good_moral',
            purpose=purpose,
            payment_amount=40.00,  # Good Moral Character fee
        )
        
        messages.success(request, f"Request submitted successfully! Your request ID is {cert_request.request_id}. Please proceed to payment.")
        
        # Redirect to payment mode selection
        return redirect('accounts:payment_mode_selection', request_id=cert_request.request_id)
    
    context = {
        'user': user,
        'unread_count': unread_count,
    }
    return render(request, 'accounts/brgy_goodmoral_character.html', context)


@login_required(login_url='accounts:login')
@never_cache
def brgy_business_cert(request):
    user = request.user
    unread_count = Announcement.objects.filter(is_active=True).count()
    
    if request.method == 'POST':
        purpose = request.POST.get('purpose')
        business_name = request.POST.get('business_name')
        business_type = request.POST.get('business_type')
        business_nature = request.POST.get('business_nature')
        business_address = request.POST.get('business_address')
        employees_count = request.POST.get('employees_count')
        
        # Validate all required fields
        if not purpose or len(purpose.strip()) < 10:
            messages.error(request, "Please provide a detailed purpose for your request (at least 10 characters).")
            context = {
                'user': user,
            }
            return render(request, 'accounts/brgy_business_cert.html', context)
        
        if not business_name or not business_type or not business_nature or not business_address or not employees_count:
            messages.error(request, "Please fill in all required business information fields.")
            context = {
                'user': user,
            }
            return render(request, 'accounts/brgy_business_cert.html', context)
        
        try:
            employees_count = int(employees_count)
            if employees_count < 0:
                raise ValueError("Number of employees cannot be negative")
        except ValueError:
            messages.error(request, "Please enter a valid number of employees.")
            context = {
                'user': user,
            }
            return render(request, 'accounts/brgy_business_cert.html', context)
        
        # Create the certificate request
        cert_request = CertificateRequest.objects.create(
            user=user,
            certificate_type='business_clearance',
            purpose=purpose,
            business_name=business_name,
            business_type=business_type,
            business_nature=business_nature,
            business_address=business_address,
            employees_count=employees_count,
            payment_amount=100.00,  # Barangay Business Clearance fee
        )
        
        messages.success(request, f"Request submitted successfully! Your request ID is {cert_request.request_id}. Please proceed to payment.")
        
        # Redirect to payment mode selection
        return redirect('accounts:payment_mode_selection', request_id=cert_request.request_id)
    
    context = {
        'user': user,
        'unread_count': unread_count,
    }
    return render(request, 'accounts/brgy_business_cert.html', context)


@login_required(login_url='accounts:login')
@never_cache
def payment_mode_selection(request, request_id):
    user = request.user
    unread_count = Announcement.objects.filter(is_active=True).count()
    
    # Get the certificate request
    cert_request = get_object_or_404(CertificateRequest, request_id=request_id, user=user)
    
    # Check if already paid
    if cert_request.payment_status == 'paid':
        messages.info(request, "This request has already been paid.")
        return redirect('accounts:certificate_requests')
    
    if request.method == 'POST':
        payment_mode = request.POST.get('payment_mode')
        
        # Validate payment mode
        if payment_mode not in ['gcash', 'counter']:
            messages.error(request, "Invalid payment mode selected.")
            context = {
                'user': user,
                'cert_request': cert_request,
            }
            return render(request, 'accounts/payment_mode_selection.html', context)
        
        # Update certificate request with payment mode
        cert_request.payment_mode = payment_mode
        cert_request.save()
        
        # Redirect based on payment mode
        if payment_mode == 'gcash':
            return redirect('accounts:gcash_payment', request_id=cert_request.request_id)
        else:  # counter
            return redirect('accounts:counter_payment', request_id=cert_request.request_id)
    
    context = {
        'user': user,
        'cert_request': cert_request,
        'unread_count': unread_count,
    }
    return render(request, 'accounts/payment_mode_selection.html', context)


@login_required(login_url='accounts:login')
@never_cache
def gcash_payment(request, request_id):
    user = request.user
    unread_count = Announcement.objects.filter(is_active=True).count()
    
    # Get the certificate request
    cert_request = get_object_or_404(CertificateRequest, request_id=request_id, user=user)
    
    # Check if already paid
    if cert_request.payment_status == 'paid':
        messages.info(request, "This request has already been paid.")
        return redirect('accounts:certificate_requests')
    
    # Verify payment mode is GCash
    if cert_request.payment_mode != 'gcash':
        messages.error(request, "Invalid payment mode for this request.")
        return redirect('accounts:payment_mode_selection', request_id=request_id)
    
    if request.method == 'POST':
        reference_number = request.POST.get('reference_number', '').strip()
        
        # Validate reference number
        if not reference_number:
            messages.error(request, "Please enter your GCash reference number.")
            context = {
                'user': user,
                'cert_request': cert_request,
            }
            return render(request, 'accounts/gcash_payment.html', context)
        
        if len(reference_number) < 10:
            messages.error(request, "Invalid reference number. Please check and try again.")
            context = {
                'user': user,
                'cert_request': cert_request,
            }
            return render(request, 'accounts/gcash_payment.html', context)
        
        # Save reference number and update status to pending verification
        cert_request.payment_reference = reference_number
        cert_request.payment_status = 'pending'  # Wait for admin verification
        cert_request.save()
        
        messages.success(request, 
            f"Payment reference submitted successfully! Your reference number {reference_number} "
            "is now pending verification by our staff. You will be notified once verified."
        )
        
        # Redirect to certificate requests page
        return redirect('accounts:certificate_requests')
    
    context = {
        'user': user,
        'cert_request': cert_request,
        'unread_count': unread_count,
    }
    return render(request, 'accounts/gcash_payment.html', context)


@login_required(login_url='accounts:login')
@never_cache
def counter_payment(request, request_id):
    user = request.user
    unread_count = Announcement.objects.filter(is_active=True).count()

    cert_request = get_object_or_404(CertificateRequest, request_id=request_id, user=user)

    # Already paid? Send back to list
    if cert_request.payment_status == 'paid':
        messages.info(request, "This request has already been paid.")
        return redirect('accounts:certificate_requests')

    # Ensure the mode is counter so users can proceed even if they skipped saving it
    if cert_request.payment_mode != 'counter':
        cert_request.payment_mode = 'counter'
        cert_request.save(update_fields=['payment_mode'])

    if request.method == 'POST':
        cert_request.payment_status = 'pending'
        cert_request.payment_reference = f"COUNTER-{cert_request.request_id}"
        cert_request.save(update_fields=['payment_status', 'payment_reference'])
        messages.success(request, "Your on-site payment has been scheduled. Please proceed to the cashier.")
        return redirect('accounts:certificate_requests')

    context = {
        'user': user,
        'cert_request': cert_request,
        'unread_count': unread_count,
    }
    return render(request, 'accounts/counter_payment.html', context)


@login_required(login_url='accounts:login')
@never_cache
def cancel_request(request, request_id):
    """
    View to handle cancellation of certificate requests.
    Only unpaid requests can be cancelled.
    """
    user = request.user
    cert_request = get_object_or_404(CertificateRequest, request_id=request_id, user=user)
    
    # Check if the request is eligible for cancellation (only unpaid requests)
    if cert_request.payment_status != 'unpaid':
        messages.error(request, "Only unpaid requests can be cancelled. Paid requests cannot be cancelled as we do not offer refunds.")
        return redirect('accounts:certificate_requests')
    
    # Store request ID for success message
    request_id_display = cert_request.request_id
    
    # Delete the request
    cert_request.delete()
    
    # Show success message
    messages.success(request, f"Certificate request {request_id_display} has been successfully cancelled.")
    
    # Redirect back to certificate requests page
    return redirect('accounts:certificate_requests')


@login_required(login_url='accounts:login')
@never_cache
def report_records(request):
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

    # Calculate summary statistics (always from all user reports, not filtered)
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
    return render(request, 'accounts/report_records.html', context)


@login_required(login_url='accounts:login')
@never_cache
def file_report(request):
    user = request.user
    unread_count = Announcement.objects.filter(is_active=True).count()
    
    if request.method == 'POST':
        report_type = request.POST.get('report_type')
        place = request.POST.get('place')
        message = request.POST.get('message')
        
        # Validation
        if not report_type or not place or not message:
            messages.error(request, "All fields are required. Please fill in all the information.")
            context = {
                'user': user,
            }
            return render(request, 'accounts/file_report.html', context)
        
        # Validate report type
        valid_report_types = ['Theft', 'Assault', 'Vandalism', 'Disturbance', 'Other']
        if report_type not in valid_report_types:
            messages.error(request, "Invalid report type selected.")
            context = {
                'user': user,
            }
            return render(request, 'accounts/file_report.html', context)
        
        # Validate place (minimum length)
        if len(place.strip()) < 5:
            messages.error(request, "Please provide a more detailed location (at least 5 characters).")
            context = {
                'user': user,
            }
            return render(request, 'accounts/file_report.html', context)
        
        # Validate message (minimum length)
        if len(message.strip()) < 20:
            messages.error(request, "Please provide a detailed description (at least 20 characters).")
            context = {
                'user': user,
            }
            return render(request, 'accounts/file_report.html', context)
        
        # Create the incident report
        try:
            incident = IncidentReport.objects.create(
                user=user,
                incident_type=report_type,
                place=place.strip(),
                message=message.strip(),
                status='Pending'
            )
            
            messages.success(
                request, 
                f"Report submitted successfully! Your report ID is {incident.report_id}. "
                "Our team will review it within 24 hours."
            )
            return redirect('accounts:report_records')
            
        except Exception as e:
            messages.error(request, f"An error occurred while submitting your report: {str(e)}")
            context = {
                'user': user,
            }
            return render(request, 'accounts/file_report.html', context)

    context = {
        'user': user,
        'unread_count': unread_count,
    }
    return render(request, 'accounts/file_report.html', context)


# -------------------- ANNOUNCEMENTS --------------------
@login_required(login_url='accounts:login')
@never_cache
def announcements(request):
    """Display active announcements for users"""
    user = request.user
    
    # Get all active announcements
    active_announcements = Announcement.objects.filter(is_active=True).order_by('-created_at')
    
    # Get unread announcement count
    unread_count = Announcement.objects.filter(is_active=True).count()
    
    context = {
        'user': user,
        'announcements': active_announcements,
        'unread_count': unread_count,
    }
    return render(request, 'accounts/announcements.html', context)


@login_required
def chatbot_api(request):
    """Handle chatbot API requests for LabangOnline"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)
    
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return JsonResponse({'error': 'Message is required'}, status=400)
        
        # Check if API key is configured
        gemini_api_key = os.environ.get('GEMINI_API_KEY', '')
        if not gemini_api_key:
            return JsonResponse({
                'error': 'AI service not configured.',
                'success': False
            }, status=500)
        
        # Configure Gemini
        genai.configure(api_key=gemini_api_key)
        
        generation_config = {
            "temperature": 0.7,
            "top_p": 1,
            "top_k": 1,
            "max_output_tokens": 2048,
        }
        
        # System context for LabangOnline
        context = f"""You are a helpful AI assistant for LabangOnline, the official online portal for Barangay Labangon in Cebu City, Philippines.

LabangOnline offers:
- Document Request Services (Barangay Clearance, Certificate of Residency, Certificate of Indigency, Good Moral Character Certificate, Business Clearance)
- Incident Report Filing
- Announcements and Updates
- Resident Verification Services

Current user information:
- Name: {request.user.full_name}
- Username: {request.user.username}
- Resident Status: {"Verified" if request.user.resident_confirmation else "Pending Verification"}
- Address: {request.user.address_line}, {request.user.barangay}, {request.user.city}

Answer questions about:
- How to request documents
- Document processing fees and requirements
- How to file incident reports
- Account and profile management
- Barangay services and procedures

Be helpful, professional, and friendly. Keep responses concise and actionable. When discussing fees or official procedures, be accurate based on the platform's actual offerings."""
        
        full_prompt = f"{context}\n\nUser: {user_message}\n\nAssistant:"
        
        # Try different models
        model_attempts = [
            'gemini-2.5-flash',
            'gemini-2.0-flash',
            'gemini-flash-latest',
            'gemini-2.5-pro',
            'gemini-pro-latest',
        ]
        
        response_text = None
        for model_name in model_attempts:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(
                    full_prompt,
                    generation_config=generation_config
                )
                response_text = response.text
                print(f"✓ SUCCESS with model: {model_name}")
                break
            except Exception as e:
                error_msg = str(e)[:150]
                print(f"✗ Model '{model_name}' failed: {error_msg}")
                continue
        
        if not response_text:
            return JsonResponse({
                'error': 'Could not generate response. Please try again.',
                'success': False
            }, status=500)
        
        return JsonResponse({
            'response': response_text,
            'success': True
        })
        
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        return JsonResponse({
            'error': 'Invalid request format',
            'success': False
        }, status=400)
    
    except Exception as e:
        print(f"Chatbot API error: {type(e).__name__}: {e}")
        import traceback
        print(f"Full traceback:\n{traceback.format_exc()}")
        return JsonResponse({
            'error': f'An error occurred: {str(e)}',
            'success': False
        }, status=500)