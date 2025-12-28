from django.urls import path
from . import views

app_name = 'administration'

urlpatterns = [
    # Dashboard
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    
    # User Management
    path('users/', views.admin_users, name='admin_users'),
    path('users/<int:user_id>/verify/', views.admin_verify_user, name='admin_verify_user'),
    path('users/<int:user_id>/deactivate/', views.admin_deactivate_user, name='admin_deactivate_user'),
    path('users/<int:user_id>/activate/', views.admin_activate_user, name='admin_activate_user'),
    path('users/change-type/', views.admin_change_user_type, name='admin_change_user_type'),
    
    # Certificate Management
    path('certificates/', views.admin_certificates, name='admin_certificates'),
    path('certificates/<str:request_id>/', views.admin_certificate_detail, name='admin_certificate_detail'),
    path('certificates/<str:request_id>/verify-payment/', views.admin_verify_payment, name='admin_verify_payment'),
    path('certificates/<str:request_id>/reject-payment/', views.admin_reject_payment, name='admin_reject_payment'),
    path('certificates/<str:request_id>/update-claim/', views.admin_update_claim_status, name='admin_update_claim_status'),
    path('certificates/<str:request_id>/delete/', views.admin_delete_certificate, name='admin_delete_certificate'),
    
    # Report Management
    path('reports/', views.admin_reports, name='admin_reports'),
    path('reports/<str:report_id>/', views.admin_report_detail, name='admin_report_detail'),
    path('reports/<str:report_id>/update-status/', views.admin_update_report_status, name='admin_update_report_status'),
    path('reports/<str:report_id>/delete/', views.admin_delete_report, name='admin_delete_report'),
    
    # Announcement Management
    path('announcements/', views.admin_announcements, name='admin_announcements'),
    path('announcements/create/', views.admin_create_announcement, name='admin_create_announcement'),
    path('announcements/<int:announcement_id>/edit/', views.admin_edit_announcement, name='admin_edit_announcement'),
    path('announcements/<int:announcement_id>/delete/', views.admin_delete_announcement, name='admin_delete_announcement'),
    path('announcements/<int:announcement_id>/toggle/', views.admin_toggle_announcement, name='admin_toggle_announcement'),
]