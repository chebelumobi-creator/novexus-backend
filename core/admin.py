# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.urls import path
from django.shortcuts import redirect, get_object_or_404
from django.http import HttpResponseRedirect
from django.utils.html import format_html
from .models import User, Transaction, SystemSettings, OTP, IMF, AccountRestriction, UserSecuritySettings


class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ['email', 'username', 'balance', 'is_verified', 'is_active']
    list_editable = ['balance', 'is_verified', 'is_active']
    fieldsets = UserAdmin.fieldsets + (
        ('Banking Info', {
            'fields': ('phone', 'address', 'profile_photo', 'balance', 'daily_transfer_limit', 'transaction_pin', 'account_number', 'is_verified')
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Banking Info', {
            'fields': ('email', 'phone', 'address', 'profile_photo', 'balance', 'daily_transfer_limit', 'transaction_pin', 'account_number', 'is_verified')
        }),
    )


class TransactionAdmin(admin.ModelAdmin):
    list_display = ['id', 'sender', 'recipient_name', 'recipient_bank', 'amount', 'status', 'transfer_type', 'created_at']
    list_filter = ['status', 'transaction_type', 'transfer_type', 'created_at']
    search_fields = ['sender__email', 'recipient_name', 'recipient_bank', 'reference']
    list_editable = ['recipient_name', 'recipient_bank', 'status']
    
    # Read-only fields that should never be changed
    readonly_fields = ['id', 'reference', 'sender', 'created_at']  # ← REMOVED 'updated_at'
    
    # Fields to show in the edit form
    fieldsets = (
        ('Transaction Details', {
            'fields': (
                'id',
                'reference',
                'sender',
                'recipient_name',
                'recipient_email',
                'recipient_bank',
                'recipient_account',
                'amount',
                'equivalent_amount',  # ← ADD
                'target_currency',    # ← ADD
                'currency_symbol',    # ← ADD
                'status',
                'transfer_type',
                'transaction_type',
            )
        }),
        ('Additional Information', {
            'fields': (
                'description',
                'swift_code',
                'country',
                'created_at',
            )
        }),
    )
    
    # Actions
    actions = ['mark_as_completed', 'mark_as_pending', 'mark_as_failed']
    
    def mark_as_completed(self, request, queryset):
        updated = queryset.update(status='completed')
        self.message_user(request, f'{updated} transaction(s) marked as completed.')
    mark_as_completed.short_description = 'Mark selected transactions as COMPLETED'
    
    def mark_as_pending(self, request, queryset):
        updated = queryset.update(status='pending')
        self.message_user(request, f'{updated} transaction(s) marked as pending.')
    mark_as_pending.short_description = 'Mark selected transactions as PENDING'
    
    def mark_as_failed(self, request, queryset):
        updated = queryset.update(status='failed')
        self.message_user(request, f'{updated} transaction(s) marked as failed.')
    mark_as_failed.short_description = 'Mark selected transactions as FAILED'


class SystemSettingsAdmin(admin.ModelAdmin):
    list_display = ['pending_button', 'otp_button', 'imf_button', 'updated_at']
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('toggle-pending/', self.admin_site.admin_view(self.toggle_pending), name='toggle-pending'),
            path('toggle-otp/', self.admin_site.admin_view(self.toggle_otp), name='toggle-otp'),
            path('toggle-imf/', self.admin_site.admin_view(self.toggle_imf), name='toggle-imf'),
        ]
        return custom_urls + urls
    
    def pending_button(self, obj):
        if obj.pending_approval_enabled:
            color = "green"
            status = "ON"
        else:
            color = "red"
            status = "OFF"
        
        return format_html(
            '<a class="button" href="{}" style="background: {}; color: white; padding: 5px 10px; text-decoration: none; border-radius: 4px; margin: 2px; display: inline-block;">Pending: {}</a>',
            'toggle-pending/',
            color,
            status
        )
    pending_button.short_description = 'Pending Approval'
    
    def otp_button(self, obj):
        if obj.otp_enabled:
            color = "green"
            status = "ON"
        else:
            color = "red"
            status = "OFF"
        
        return format_html(
            '<a class="button" href="{}" style="background: {}; color: white; padding: 5px 10px; text-decoration: none; border-radius: 4px; margin: 2px; display: inline-block;">OTP: {}</a>',
            'toggle-otp/',
            color,
            status
        )
    otp_button.short_description = 'OTP'
    
    def imf_button(self, obj):
        if obj.imf_enabled:
            color = "green"
            status = "ON"
        else:
            color = "red"
            status = "OFF"
        
        return format_html(
            '<a class="button" href="{}" style="background: {}; color: white; padding: 5px 10px; text-decoration: none; border-radius: 4px; margin: 2px; display: inline-block;">IMF: {}</a>',
            'toggle-imf/',
            color,
            status
        )
    imf_button.short_description = 'IMF'
    
    def toggle_pending(self, request):
        settings = SystemSettings.objects.first()
        settings.pending_approval_enabled = not settings.pending_approval_enabled
        settings.save()
        return redirect('admin:core_systemsettings_changelist')
    
    def toggle_otp(self, request):
        settings = SystemSettings.objects.first()
        settings.otp_enabled = not settings.otp_enabled
        settings.save()
        return redirect('admin:core_systemsettings_changelist')
    
    def toggle_imf(self, request):
        settings = SystemSettings.objects.first()
        settings.imf_enabled = not settings.imf_enabled
        settings.save()
        return redirect('admin:core_systemsettings_changelist')
    
    def has_add_permission(self, request):
        if self.model.objects.exists():
            return False
        return True


class OTPAdmin(admin.ModelAdmin):
    list_display = ['user', 'code', 'created_at', 'is_used', 'transaction_id']
    list_filter = ['is_used', 'created_at']
    search_fields = ['user__email', 'code']
    readonly_fields = ['user', 'code', 'created_at', 'transaction_id']


class IMFAdmin(admin.ModelAdmin):
    list_display = ['user', 'code', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['user__email', 'code']
    
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['user', 'code', 'created_at']
        return []


class AccountRestrictionAdmin(admin.ModelAdmin):
    list_display = ['user', 'is_restricted', 'reason', 'restricted_at']
    list_filter = ['is_restricted']
    search_fields = ['user__email', 'reason']
    list_editable = ['is_restricted', 'reason']


class UserSecuritySettingsAdmin(admin.ModelAdmin):
    list_display = ['user_email', 'pending_button', 'otp_button', 'imf_button', 'manual_verification_button', 'restricted_button', 'updated_at']
    list_per_page = 20
    search_fields = ['user__email', 'user__username']
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('toggle-pending/<int:user_id>/', self.admin_site.admin_view(self.toggle_pending), name='toggle-user-pending'),
            path('toggle-otp/<int:user_id>/', self.admin_site.admin_view(self.toggle_otp), name='toggle-user-otp'),
            path('toggle-imf/<int:user_id>/', self.admin_site.admin_view(self.toggle_imf), name='toggle-user-imf'),
            path('toggle-manual-verification/<int:user_id>/', self.admin_site.admin_view(self.toggle_manual_verification), name='toggle-user-manual-verification'),
            path('toggle-restricted/<int:user_id>/', self.admin_site.admin_view(self.toggle_restricted), name='toggle-user-restricted'),
        ]
        return custom_urls + urls
    
    def user_email(self, obj):
        return format_html('<strong>{}</strong>', obj.user.email)
    user_email.short_description = 'User'
    
    def pending_button(self, obj):
        if obj.pending_approval_enabled:
            return format_html(
                '<a class="button" href="toggle-pending/{}/" style="background: green; color: white; padding: 5px 10px; text-decoration: none; border-radius: 4px; margin: 2px; display: inline-block;">✅ Pending: ON</a>',
                obj.user.id
            )
        else:
            return format_html(
                '<a class="button" href="toggle-pending/{}/" style="background: gray; color: white; padding: 5px 10px; text-decoration: none; border-radius: 4px; margin: 2px; display: inline-block;">⭕ Pending: OFF</a>',
                obj.user.id
            )
    pending_button.short_description = 'Pending Approval'
    
    def otp_button(self, obj):
        if obj.otp_enabled:
            return format_html(
                '<a class="button" href="toggle-otp/{}/" style="background: green; color: white; padding: 5px 10px; text-decoration: none; border-radius: 4px; margin: 2px; display: inline-block;">🔐 OTP: ON</a>',
                obj.user.id
            )
        else:
            return format_html(
                '<a class="button" href="toggle-otp/{}/" style="background: gray; color: white; padding: 5px 10px; text-decoration: none; border-radius: 4px; margin: 2px; display: inline-block;">🔓 OTP: OFF</a>',
                obj.user.id
            )
    otp_button.short_description = 'OTP'
    
    def imf_button(self, obj):
        if obj.imf_enabled:
            return format_html(
                '<a class="button" href="toggle-imf/{}/" style="background: green; color: white; padding: 5px 10px; text-decoration: none; border-radius: 4px; margin: 2px; display: inline-block;">🆔 IMF: ON</a>',
                obj.user.id
            )
        else:
            return format_html(
                '<a class="button" href="toggle-imf/{}/" style="background: gray; color: white; padding: 5px 10px; text-decoration: none; border-radius: 4px; margin: 2px; display: inline-block;">🆔 IMF: OFF</a>',
                obj.user.id
            )
    imf_button.short_description = 'IMF'
    
    def manual_verification_button(self, obj):
        if obj.manual_verification_enabled:
            return format_html(
                '<a class="button" href="toggle-manual-verification/{}/" style="background: orange; color: white; padding: 5px 10px; text-decoration: none; border-radius: 4px; margin: 2px; display: inline-block;">⚠️ Manual: ON</a>',
                obj.user.id
            )
        else:
            return format_html(
                '<a class="button" href="toggle-manual-verification/{}/" style="background: gray; color: white; padding: 5px 10px; text-decoration: none; border-radius: 4px; margin: 2px; display: inline-block;">⚪ Manual: OFF</a>',
                obj.user.id
            )
    manual_verification_button.short_description = 'Manual Verification'
    
    def restricted_button(self, obj):
        if obj.is_restricted:
            return format_html(
                '<a class="button" href="toggle-restricted/{}/" style="background: red; color: white; padding: 5px 10px; text-decoration: none; border-radius: 4px; margin: 2px; display: inline-block;">🚫 Restricted: YES</a>',
                obj.user.id
            )
        else:
            return format_html(
                '<a class="button" href="toggle-restricted/{}/" style="background: green; color: white; padding: 5px 10px; text-decoration: none; border-radius: 4px; margin: 2px; display: inline-block;">✅ Restricted: NO</a>',
                obj.user.id
            )
    restricted_button.short_description = 'Restricted'
    
    def toggle_pending(self, request, user_id):
        settings = get_object_or_404(UserSecuritySettings, user_id=user_id)
        settings.pending_approval_enabled = not settings.pending_approval_enabled
        settings.save()
        return redirect('admin:core_usersecuritysettings_changelist')
    
    def toggle_otp(self, request, user_id):
        settings = get_object_or_404(UserSecuritySettings, user_id=user_id)
        settings.otp_enabled = not settings.otp_enabled
        settings.save()
        return redirect('admin:core_usersecuritysettings_changelist')
    
    def toggle_imf(self, request, user_id):
        settings = get_object_or_404(UserSecuritySettings, user_id=user_id)
        settings.imf_enabled = not settings.imf_enabled
        settings.save()
        return redirect('admin:core_usersecuritysettings_changelist')
    
    def toggle_manual_verification(self, request, user_id):
        settings = get_object_or_404(UserSecuritySettings, user_id=user_id)
        settings.manual_verification_enabled = not settings.manual_verification_enabled
        settings.save()
        return redirect('admin:core_usersecuritysettings_changelist')
    
    def toggle_restricted(self, request, user_id):
        settings = get_object_or_404(UserSecuritySettings, user_id=user_id)
        settings.is_restricted = not settings.is_restricted
        settings.save()
        return redirect('admin:core_usersecuritysettings_changelist')
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


# Register all models
admin.site.register(User, CustomUserAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(SystemSettings, SystemSettingsAdmin)
admin.site.register(OTP, OTPAdmin)
admin.site.register(IMF, IMFAdmin)
admin.site.register(AccountRestriction, AccountRestrictionAdmin)
admin.site.register(UserSecuritySettings, UserSecuritySettingsAdmin)