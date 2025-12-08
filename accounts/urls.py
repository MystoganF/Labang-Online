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
    path('report-detail/<str:report_id>/', views.report_detail, name='report_detail'),

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
    
    

    # Admin/Dashboard
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),

    # User Management URLs
    path('admin/users/', views.admin_users, name='admin_users'),
    path('admin/users/<int:user_id>/verify/', views.admin_verify_user, name='admin_verify_user'),
    path('admin/users/<int:user_id>/deactivate/', views.admin_deactivate_user, name='admin_deactivate_user'),
    path('admin/users/<int:user_id>/activate/', views.admin_activate_user, name='admin_activate_user'),
    path('admin/users/change-type/', views.admin_change_user_type, name='admin_change_user_type'),

    # Certificate Management URLs
    path('admin/certificates/', views.admin_certificates, name='admin_certificates'),
    path('admin/certificates/<str:request_id>/', views.admin_certificate_detail, name='admin_certificate_detail'),
    path('admin/certificates/<str:request_id>/verify-payment/', views.admin_verify_payment, name='admin_verify_payment'),
    path('admin/certificates/<str:request_id>/reject-payment/', views.admin_reject_payment, name='admin_reject_payment'),
    path('admin/certificates/<str:request_id>/update-claim/', views.admin_update_claim_status, name='admin_update_claim_status'),
    path('admin/certificates/<str:request_id>/delete/', views.admin_delete_certificate, name='admin_delete_certificate'),

    # Report Management URLs
    path('admin/reports/', views.admin_reports, name='admin_reports'),
    path('admin/reports/<str:report_id>/', views.admin_report_detail, name='admin_report_detail'),
    path('admin/reports/<str:report_id>/update-status/', views.admin_update_report_status, name='admin_update_report_status'),
    path('admin/reports/<str:report_id>/delete/', views.admin_delete_report, name='admin_delete_report'),

    # User Announcements (Notifications)
    path('announcements/', views.announcements, name='announcements'),
    
    # Admin Announcement Management
    path('admin/announcements/', views.admin_announcements, name='admin_announcements'),
    path('admin/announcements/create/', views.admin_create_announcement, name='admin_create_announcement'),
    path('admin/announcements/<int:announcement_id>/edit/', views.admin_edit_announcement, name='admin_edit_announcement'),
    path('admin/announcements/<int:announcement_id>/delete/', views.admin_delete_announcement, name='admin_delete_announcement'),
    path('admin/announcements/<int:announcement_id>/toggle/', views.admin_toggle_announcement, name='admin_toggle_announcement'),
    
    # Admin/Dashboard
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),

    # User Management URLs
    path('admin/users/', views.admin_users, name='admin_users'),
    path('admin/users/<int:user_id>/verify/', views.admin_verify_user, name='admin_verify_user'),
    path('admin/users/<int:user_id>/deactivate/', views.admin_deactivate_user, name='admin_deactivate_user'),
    path('admin/users/<int:user_id>/activate/', views.admin_activate_user, name='admin_activate_user'),
    

    # Certificate Management URLs
    path('admin/certificates/', views.admin_certificates, name='admin_certificates'),
    path('admin/certificates/<str:request_id>/', views.admin_certificate_detail, name='admin_certificate_detail'),
    path('admin/certificates/<str:request_id>/verify-payment/', views.admin_verify_payment, name='admin_verify_payment'),
    path('admin/certificates/<str:request_id>/reject-payment/', views.admin_reject_payment, name='admin_reject_payment'),
    path('admin/certificates/<str:request_id>/update-claim/', views.admin_update_claim_status, name='admin_update_claim_status'),
    path('admin/certificates/<str:request_id>/delete/', views.admin_delete_certificate, name='admin_delete_certificate'),

    # Report Management URLs
    path('admin/reports/', views.admin_reports, name='admin_reports'),
    path('admin/reports/<str:report_id>/', views.admin_report_detail, name='admin_report_detail'),
    path('admin/reports/<str:report_id>/update-status/', views.admin_update_report_status, name='admin_update_report_status'),
    path('admin/reports/<str:report_id>/delete/', views.admin_delete_report, name='admin_delete_report'),

    # User Announcements (Notifications)
    path('announcements/', views.announcements, name='announcements'),
    
    # Admin Announcement Management
    path('admin/announcements/', views.admin_announcements, name='admin_announcements'),
    path('admin/announcements/create/', views.admin_create_announcement, name='admin_create_announcement'),
    path('admin/announcements/<int:announcement_id>/edit/', views.admin_edit_announcement, name='admin_edit_announcement'),
    path('admin/announcements/<int:announcement_id>/delete/', views.admin_delete_announcement, name='admin_delete_announcement'),
    path('admin/announcements/<int:announcement_id>/toggle/', views.admin_toggle_announcement, name='admin_toggle_announcement'),

    #Change user type (Resident/Admin)
    path(
        'admin/users/<int:user_id>/change-type/',
        views.admin_change_user_type,
        name='admin_change_user_type'
    ),
]

