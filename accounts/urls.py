from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # -------------------- PUBLIC PAGES --------------------
    path('', views.home, name='home'),
    path('welcome/', views.welcome, name='welcome'),
    
    # -------------------- AUTHENTICATION --------------------
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_confirm, name='logout_confirm'),
    
    # -------------------- PASSWORD RESET --------------------
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('verify-code/<int:user_id>/', views.verify_code, name='verify_code'),
    path('resend-code/<int:user_id>/', views.resend_code, name='resend_code'),
    path('reset-password/', views.reset_password, name='reset_password'),
    
    # -------------------- USER PROFILE --------------------
    path('personal-info/', views.personal_info, name='personal_info'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('complete-profile/', views.complete_profile, name='complete_profile'),
    
    # Profile update endpoints
    path('update-basic-info/', views.update_basic_info, name='update_basic_info'),
    path('update-profile-photo/', views.update_profile_photo, name='update_profile_photo'),
    path('update-resident-id/', views.update_resident_id, name='update_resident_id'),
    
    # -------------------- CHATBOT --------------------
    path('chatbot-api/', views.chatbot_api, name='chatbot_api'),
]