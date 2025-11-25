#urls.py
from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login, name='login'),
    path('forgot_password/', views.forgot_password, name='forgot_password'),
    path('verify_code/<int:user_id>/', views.verify_code, name='verify_code'),
    path('reset_password/', views.reset_password, name='reset_password'),
    path('register/', views.register, name='register'),
    path('welcome/', views.welcome, name='welcome'),
    path('logout_confirm/', views.logout_confirm, name='logout_confirm'),
    path('personal_info/', views.personal_info, name='personal_info'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('complete_profile/', views.complete_profile, name='complete_profile'),
    path('document_request/', views.document_request, name='document_request'),
    path('certificate_requests/', views.certificate_requests, name='certificate_requests'),
    path('request-detail/<str:request_id>/', views.request_detail, name='request_detail'),
    path('report_records/', views.report_records, name='report_records'),
    path('file_report/', views.file_report, name='file_report'),


    # Request pages
    path('barangay-clearance-request/', views.barangay_clearance_request, name='barangay_clearance_request'),
    path('brgy_residency_cert/', views.brgy_residency_cert, name='brgy_residency_cert'),
    path('brgy_indigency_cert/', views.brgy_indigency_cert, name='brgy_indigency_cert'),
    path('brgy_goodmoral_character/', views.brgy_goodmoral_character, name='brgy_goodmoral_character'),
    path('brgy_business_cert/', views.brgy_business_cert, name='brgy_business_cert'),

    # Payments 
    path('payment/mode-selection/<str:request_id>/', views.payment_mode_selection, name='payment_mode_selection'),
    path('gcash-payment/<str:request_id>/', views.gcash_payment, name='gcash_payment'),
    path('counter_payment/<str:request_id>/', views.counter_payment, name='counter_payment'),
    
    # Request Management
    path('certificate_requests/cancel_request/<str:request_id>/', views.cancel_request, name='cancel_request'),

    # User Announcements (Notifications)
    path('announcements/', views.announcements, name='announcements'),
    # Verify code & resend
    path('verify_code/<int:user_id>/resend/', views.resend_code, name='resend_code'),
    path('api/chatbot/', views.chatbot_api, name='chatbot_api'),
    
    
]
