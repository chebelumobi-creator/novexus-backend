
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

urlpatterns = [
    # Auth
    path('register/', views.register, name='register'),
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Profile
    path('profile/', views.profile, name='profile'),
    path('profile/update/', views.update_profile, name='update_profile'),

    # Banking
    path('transfer/', views.transfer, name='transfer'),
    path('domestic-transfer/', views.domestic_transfer, name='domestic_transfer'),
    path('wire-transfer/', views.wire_transfer, name='wire_transfer'),
    path('history/', views.transaction_history, name='history'),
    path('deposit/', views.deposit, name='deposit'),
    path('withdraw/', views.withdraw, name='withdraw'),
    path('logout/', views.logout, name='logout'),

    # Transactions
    path('transaction/<int:transaction_id>/delete/', views.delete_transaction, name='delete_transaction'),

    # ========== NEW SECURITY FEATURES ==========
    
    # OTP Verification
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('resend-otp/', views.resend_otp, name='resend_otp'),

    # Admin - Pending Approvals
    path('admin/transactions/pending/', views.get_pending_transactions, name='pending_transactions'),
    path('admin/transaction/<int:transaction_id>/approve/', views.approve_transaction, name='approve_transaction'),
    path('admin/transaction/<int:transaction_id>/reject/', views.reject_transaction, name='reject_transaction'),

    # Admin - System Settings
    path('admin/settings/', views.system_settings, name='system_settings'),

    # Admin - IMF Management
    path('admin/imf/', views.manage_imf, name='manage_imf'),
    path('admin/imf/<int:user_id>/', views.manage_imf, name='manage_imf_user'),

    # Admin - Account Restriction
    path('admin/restrict-user/<int:user_id>/', views.restrict_account, name='restrict_account'),
]