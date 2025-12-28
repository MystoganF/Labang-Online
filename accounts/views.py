"""
accounts/views.py
Handles user authentication, registration, and profile management
"""

from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt

from .models import User, PasswordResetCode
from .forms import RegistrationForm

import json
import os
import google.generativeai as genai


# -------------------- PUBLIC PAGES --------------------

@never_cache
def home(request: HttpRequest) -> HttpResponse:
    """Public landing page with sections, always accessible."""
    return render(request, 'home.html')


def welcome(request: HttpRequest) -> HttpResponse:
    """Welcome page"""
    return render(request, 'accounts/welcome.html')


# -------------------- AUTHENTICATION --------------------

@never_cache
def login(request):
    """User login view"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.resident_confirmation:
                auth_login(request, user)
                # Redirect based on user type
                if user.is_superuser:
                    return redirect('administration:admin_dashboard')
                else:
                    return redirect('accounts:personal_info')
            else:
                messages.warning(
                    request, 
                    "Account verification pending. Please visit Barangay Hall of Labangon to complete your account verification."
                )
        else:
            messages.error(
                request, 
                "Invalid credentials. Please check your username and password and try again."
            )

    return render(request, 'accounts/login.html')


@never_cache
def register(request):
    """User registration view"""
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
            messages.error(
                request, 
                "This email address is already registered. Please use a different email or log in to your existing account."
            )
            return render(request, "accounts/register.html")
        
        if User.objects.filter(username=username).exists():
            messages.error(
                request, 
                "This username is already taken. Please choose a different username."
            )
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

        messages.success(
            request, 
            "Account created successfully! Please proceed to Barangay Hall of Labangon for verification."
        )
        return redirect("accounts:login")

    return render(request, "accounts/register.html")


@login_required(login_url='accounts:login')
@never_cache
def logout_confirm(request):
    """Logout confirmation and execution"""
    storage = messages.get_messages(request)
    storage.used = True
    
    if request.method == 'POST':
        auth_logout(request)
        messages.success(request, "You have successfully logged out.")
        return redirect('accounts:login')
    
    return render(request, 'accounts/logout_confirm.html')


# -------------------- PASSWORD RESET --------------------

def forgot_password(request):
    """Password reset request view"""
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
                messages.success(
                    request, 
                    f"Verification code sent to {email}. Please check your email and enter the 6-digit code."
                )
                request.session['verification_code'] = reset_code.code
                return redirect('accounts:verify_code', user_id=user.id)
            except Exception as e:
                messages.error(
                    request, 
                    f"Failed to send email. Please try again later. Error: {str(e)}"
                )
                
        except User.DoesNotExist:
            messages.success(
                request, 
                f"If an account exists with {email}, a verification code has been sent."
            )
            return redirect('accounts:login')
    
    return render(request, 'accounts/forgot_password.html')


def verify_code(request, user_id):
    """Verify password reset code"""
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
                request.session['reset_code_id'] = reset_code.id
                if 'verification_code' in request.session:
                    del request.session['verification_code']
                messages.success(
                    request, 
                    "Code verified successfully! Please enter your new password."
                )
                return redirect('accounts:reset_password')
            else:
                messages.error(request, "Code has expired. Please request a new code.")
                return redirect('accounts:forgot_password')
                
        except PasswordResetCode.DoesNotExist:
            messages.error(request, "Invalid verification code. Please try again.")
    
    verification_code = request.session.get('verification_code', None)
    context = {
        'user': user, 
        'hide_user_nav': True, 
        'verification_code': verification_code
    }
    return render(request, 'accounts/verify_code.html', context)


def resend_code(request, user_id):
    """Resend verification code"""
    user = get_object_or_404(User, id=user_id)
    
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
        request.session['verification_code'] = reset_code.code
    except Exception as e:
        messages.error(
            request, 
            f"Failed to send email. Please try again later. Error: {str(e)}"
        )
    
    return redirect('accounts:verify_code', user_id=user.id)


def reset_password(request):
    """Reset password with verified code"""
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
        
        messages.success(
            request, 
            "Password updated successfully! You can now log in with your new password."
        )
        return redirect('accounts:login')
    
    return render(request, 'accounts/reset_password.html')


# -------------------- USER PROFILE --------------------

@login_required(login_url='accounts:login')
@never_cache
def personal_info(request):
    """User personal information page"""
    storage = messages.get_messages(request)
    storage.used = True

    user = request.user
    
    # Import here to avoid circular dependency
    from announcements.models import Announcement
    unread_count = Announcement.objects.filter(is_active=True).count()

    context = {
        'user': user,
        'unread_count': unread_count,
    }   
    return render(request, 'accounts/personal_info.html', context)


@login_required(login_url='accounts:login')
@never_cache
def edit_profile(request):
    """Edit user profile"""
    user = request.user
    
    # Import here to avoid circular dependency
    from announcements.models import Announcement
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
        from accounts.storage_utils import upload_to_supabase, delete_from_supabase
        
        profile_photo = request.FILES.get('profile_photo')
        if profile_photo:
            if user.profile_photo_url:
                delete_from_supabase(user.profile_photo_url, bucket_name='user-uploads')
            
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
            if user.resident_id_photo_url:
                delete_from_supabase(user.resident_id_photo_url, bucket_name='user-uploads')
            
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
            context = {'user': user}
            return render(request, 'accounts/edit_profile.html', context)

    context = {
        'user': user,
        'unread_count': unread_count,
    }
    return render(request, 'accounts/edit_profile.html', context)


@login_required(login_url='accounts:login')
@never_cache
def complete_profile(request):
    """View complete profile information"""
    user = request.user
    dependents = []
    
    context = {
        'user': user,
        'dependents': dependents,
    }
    return render(request, 'accounts/complete_profile.html', context)


# -------------------- CHATBOT --------------------

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