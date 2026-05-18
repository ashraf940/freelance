from django.urls import path
from . import views

urlpatterns = [
    # Frontend URLs (Templates)
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile_view, name='edit-profile'),
    path('change-password/', views.change_password_view, name='change-password'),
    
    # Forgot Password - OTP Based (YEH 3 URLS ADD KIYE HAIN)
    path('forgot-password/', views.forgot_password_view, name='forgot-password'),
    path('verify-reset-otp/', views.verify_reset_otp_view, name='verify-reset-otp'),
    path('resend-reset-otp/', views.resend_reset_otp_view, name='resend-reset-otp'),
    path('set-new-password/', views.set_new_password_view, name='set-new-password'),
    
    # Old reset password (token based) - agar chahiye to rakho
    # path('reset-password/<uuid:token>/', views.reset_password_view, name='reset-password'),
    
    path('verify-email/<uuid:token>/', views.verify_email_view, name='verify-email'),
    
    # API URLs (For Swagger/Postman)
    path('api/register/', views.APIRegisterView.as_view(), name='api-register'),
    path('api/login/', views.APILoginView.as_view(), name='api-login'),
    path('api/logout/', views.APILogoutView.as_view(), name='api-logout'),
    path('api/profile/', views.APIProfileView.as_view(), name='api-profile'),
    path('api/change-password/', views.APIChangePasswordView.as_view(), name='api-change-password'),
    path('api/forgot-password/', views.APIForgotPasswordView.as_view(), name='api-forgot-password'),
    path('api/reset-password/', views.APIResetPasswordView.as_view(), name='api-reset-password'),
    path('api/refresh-token/', views.APIRefreshTokenView.as_view(), name='api-refresh-token'),
]