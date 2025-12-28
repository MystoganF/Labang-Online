from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib import admin
from .models import User, PasswordResetCode
from certificates.models import CertificateRequest
from reports.models import IncidentReport
from announcements.models import Announcement

# Your admin registrations here...

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        'username', 'full_name', 'email', 'contact_number',
        'barangay', 'is_active', 'is_staff', 'resident_confirmation',
        'date_joined'
    )
    list_filter = (
        'is_staff', 'is_superuser', 'is_active', 'resident_confirmation',
        'barangay', 'civil_status', 'date_joined'
    )
    search_fields = ('username', 'full_name', 'email', 'contact_number', 'address_line')
    ordering = ('-date_joined',)
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Profile Information', {
            'fields': ('full_name', 'contact_number', 'date_of_birth', 'civil_status')
        }),
        ('Address Information', {
            'fields': ('address_line', 'barangay', 'city', 'province', 'postal_code')
        }),
        ('Verification', {
            'fields': ('resident_confirmation', 'profile_photo_url', 'resident_id_photo_url')
        }),
    )

@admin.register(PasswordResetCode)
class PasswordResetCodeAdmin(admin.ModelAdmin):
    list_display = ('user', 'code', 'created_at', 'expires_at', 'is_used', 'is_valid')
    list_filter = ('is_used', 'created_at')
    search_fields = ('user__username', 'user__email', 'code')
    readonly_fields = ('created_at', 'expires_at')
    
    def is_valid(self, obj):
        return obj.is_valid()
    is_valid.boolean = True
    is_valid.short_description = 'Valid'

@admin.register(CertificateRequest)
class CertificateRequestAdmin(admin.ModelAdmin):
    list_display = (
        'request_id', 'user', 'certificate_type', 'payment_status',
        'claim_status', 'payment_amount', 'created_at', 'paid_at'
    )
    list_filter = (
        'certificate_type', 'payment_status', 'claim_status',
        'payment_mode', 'created_at', 'paid_at'
    )
    search_fields = ('request_id', 'user__username', 'user__full_name', 'purpose')
    readonly_fields = ('request_id', 'created_at', 'updated_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Request Information', {
            'fields': ('request_id', 'user', 'certificate_type', 'purpose')
        }),
        ('Business Details', {
            'fields': ('business_name', 'business_type', 'business_nature', 'business_address', 'employees_count'),
            'classes': ('collapse',)
        }),
        ('Payment Information', {
            'fields': ('payment_status', 'payment_mode', 'payment_amount', 'payment_reference', 'paid_at')
        }),
        ('Claim Status', {
            'fields': ('claim_status', 'claimed_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(IncidentReport)
class IncidentReportAdmin(admin.ModelAdmin):
    list_display = ('report_id', 'user', 'incident_type', 'place', 'status', 'created_at')
    list_filter = ('incident_type', 'status', 'created_at')
    search_fields = ('report_id', 'user__username', 'user__full_name', 'place', 'message')
    readonly_fields = ('report_id', 'created_at')
    ordering = ('-created_at',)

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'announcement_type', 'is_active', 'posted_by', 'created_at')
    list_filter = ('announcement_type', 'is_active', 'created_at')
    search_fields = ('title', 'content', 'posted_by__username')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    
    actions = ['make_active', 'make_inactive']
    
    def make_active(self, request, queryset):
        queryset.update(is_active=True)
    make_active.short_description = "Mark selected announcements as active"
    
    def make_inactive(self, request, queryset):
        queryset.update(is_active=False)
    make_inactive.short_description = "Mark selected announcements as inactive"
