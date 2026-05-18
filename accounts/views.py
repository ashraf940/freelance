from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .models import User, EmailVerificationToken, PasswordResetToken
import random
import uuid

# ========== HELPER FUNCTIONS ==========

def generate_otp():
    """Generate 6-digit OTP"""
    return str(random.randint(100000, 999999))

# ========== TEMPLATE VIEWS (Frontend) ==========

def register_view(request):
    if request.user.is_authenticated:
        return redirect('profile')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        role = request.POST.get('role')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        
        if password != password2:
            messages.error(request, 'Passwords do not match')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
        elif len(password) < 8:
            messages.error(request, 'Password must be at least 8 characters')
        else:
            user = User.objects.create_user(
                email=email,
                username=username,
                first_name=first_name,
                last_name=last_name,
                role=role,
                password=password
            )
            user.email_verified = True
            user.save()
            
            messages.success(request, 'Account created! Please login.')
            return redirect('login')
    
    return render(request, 'accounts/register.html')

def login_view(request):
    if request.user.is_authenticated:
        return redirect('gigs:gig_list')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back!')
            return redirect('gigs:gig_list')
        else:
            messages.error(request, 'Invalid email or password')
    
    return render(request, 'accounts/login.html')

@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html', {'user': request.user})

@login_required
def edit_profile_view(request):
    if request.method == 'POST':
        user = request.user
        
        # Name update
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.bio = request.POST.get('bio', '')
        
        # Username update
        new_username = request.POST.get('username')
        if new_username and new_username != user.username:
            if not User.objects.filter(username=new_username).exists():
                user.username = new_username
            else:
                messages.error(request, 'Username already taken')
        
        # Avatar upload
        avatar_file = request.FILES.get('avatar')
        print("AVATAR FILE:", avatar_file)  # ← debug ke liye
        if avatar_file:
            import os
            os.makedirs(os.path.join(settings.MEDIA_ROOT, 'avatars'), exist_ok=True)
            if user.avatar:
                user.avatar.delete(save=False)
            user.avatar = avatar_file
            print("AVATAR SAVED:", user.avatar)  # ← debug
        
        user.save()
        messages.success(request, 'Profile updated!')
        return redirect('profile')
    
    return render(request, 'accounts/edit_profile.html', {'user': request.user})

@login_required
def change_password_view(request):
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if not request.user.check_password(old_password):
            messages.error(request, 'Current password is incorrect')
        elif new_password != confirm_password:
            messages.error(request, 'New passwords do not match')
        elif len(new_password) < 8:
            messages.error(request, 'Password must be at least 8 characters')
        else:
            request.user.set_password(new_password)
            request.user.save()
            messages.success(request, 'Password changed! Please login again.')
            logout(request)
            return redirect('login')
    
    return render(request, 'accounts/change_password.html')

def forgot_password_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            token = PasswordResetToken.objects.create(user=user)
            reset_link = request.build_absolute_uri(f'/accounts/reset-password/{token.token}/')
            messages.success(request, 'Reset link sent to your email!')
        except User.DoesNotExist:
            messages.warning(request, 'No account found with this email')
    
    return render(request, 'accounts/forgot_password.html')

def reset_password_view(request, token):
    try:
        reset_token = PasswordResetToken.objects.get(token=token, is_used=False)
        
        if request.method == 'POST':
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
            
            if new_password != confirm_password:
                messages.error(request, 'Passwords do not match')
            elif len(new_password) < 8:
                messages.error(request, 'Password must be at least 8 characters')
            else:
                user = reset_token.user
                user.set_password(new_password)
                user.save()
                reset_token.is_used = True
                reset_token.save()
                messages.success(request, 'Password reset successful! Please login.')
                return redirect('login')
        
        return render(request, 'accounts/reset_password.html', {'token': token})
    except PasswordResetToken.DoesNotExist:
        messages.error(request, 'Invalid or expired reset link')
        return redirect('forgot-password')

def verify_email_view(request, token):
    try:
        ver_token = EmailVerificationToken.objects.get(token=token)
        user = ver_token.user
        user.email_verified = True
        user.save()
        ver_token.delete()
        messages.success(request, 'Email verified! You can now login.')
    except EmailVerificationToken.DoesNotExist:
        messages.error(request, 'Invalid verification link')
    
    return redirect('login')

def logout_view(request):
    logout(request)
    messages.success(request, 'Logged out successfully!')
    return redirect('login')


# ========== API VIEWS (For Swagger/Postman) ==========

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .serializers import (
    UserSerializer, RegisterSerializer, LoginSerializer,
    ChangePasswordSerializer, ForgotPasswordSerializer,
    ResetPasswordSerializer, ProfileUpdateSerializer
)

class APIRegisterView(APIView):
    permission_classes = [permissions.AllowAny]
    
    @swagger_auto_schema(
        request_body=RegisterSerializer,
        responses={201: UserSerializer(), 400: 'Bad Request'},
        operation_description="Register a new user account",
        tags=['Authentication']
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'success': True,
                'message': 'Registration successful',
                'user': UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class APILoginView(APIView):
    permission_classes = [permissions.AllowAny]
    
    @swagger_auto_schema(
        request_body=LoginSerializer,
        responses={200: 'Success', 401: 'Unauthorized'},
        operation_description="Login with email and password to get JWT tokens",
        tags=['Authentication']
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            
            user = authenticate(username=email, password=password)
            
            if user:
                if not user.email_verified:
                    return Response({
                        'success': False,
                        'error': 'Please verify your email first'
                    }, status=status.HTTP_401_UNAUTHORIZED)
                
                refresh = RefreshToken.for_user(user)
                return Response({
                    'success': True,
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'user': UserSerializer(user).data
                })
            return Response({
                'success': False,
                'error': 'Invalid credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class APIProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(
        responses={200: UserSerializer()},
        operation_description="Get current user profile",
        tags=['Profile']
    )
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response({
            'success': True,
            'data': serializer.data
        })
    
    @swagger_auto_schema(
        request_body=ProfileUpdateSerializer,
        responses={200: UserSerializer()},
        operation_description="Update user profile",
        tags=['Profile']
    )
    def put(self, request):
        serializer = ProfileUpdateSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': 'Profile updated successfully',
                'data': serializer.data
            })
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class APIChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(
        request_body=ChangePasswordSerializer,
        responses={200: 'Success', 400: 'Bad Request'},
        operation_description="Change user password",
        tags=['Profile']
    )
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if not user.check_password(serializer.validated_data['old_password']):
                return Response({
                    'success': False,
                    'error': 'Current password is incorrect'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({
                'success': True,
                'message': 'Password changed successfully'
            })
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class APIForgotPasswordView(APIView):
    permission_classes = [permissions.AllowAny]
    
    @swagger_auto_schema(
        request_body=ForgotPasswordSerializer,
        responses={200: 'Success', 400: 'Bad Request'},
        operation_description="Request password reset link",
        tags=['Password Reset']
    )
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            
            try:
                user = User.objects.get(email=email)
                token = PasswordResetToken.objects.create(user=user)
                reset_link = request.build_absolute_uri(f'/accounts/reset-password/{token.token}/')
                
                return Response({
                    'success': True,
                    'message': 'Password reset link sent to your email',
                    'reset_link': reset_link  # For testing only
                })
            except User.DoesNotExist:
                return Response({
                    'success': True,
                    'message': 'If email exists, reset link will be sent'
                })
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class APIResetPasswordView(APIView):
    permission_classes = [permissions.AllowAny]
    
    @swagger_auto_schema(
        request_body=ResetPasswordSerializer,
        responses={200: 'Success', 400: 'Bad Request'},
        operation_description="Reset password using token",
        tags=['Password Reset']
    )
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            token = serializer.validated_data['token']
            new_password = serializer.validated_data['new_password']
            
            try:
                reset_token = PasswordResetToken.objects.get(token=token, is_used=False)
                user = reset_token.user
                user.set_password(new_password)
                user.save()
                reset_token.is_used = True
                reset_token.save()
                
                return Response({
                    'success': True,
                    'message': 'Password reset successful'
                })
            except PasswordResetToken.DoesNotExist:
                return Response({
                    'success': False,
                    'error': 'Invalid or expired token'
                }, status=status.HTTP_400_BAD_REQUEST)
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class APILogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Logout and blacklist refresh token",
        tags=['Authentication']
    )
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            return Response({
                'success': True,
                'message': 'Logged out successfully'
            })
        except Exception:
            return Response({
                'success': True,
                'message': 'Logged out'
            })

class APIRefreshTokenView(APIView):
    permission_classes = [permissions.AllowAny]
    
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'refresh': openapi.Schema(type=openapi.TYPE_STRING, description='Refresh token'),
            },
            required=['refresh']
        ),
        responses={200: 'New access token'},
        operation_description="Get new access token using refresh token",
        tags=['Authentication']
    )
    def post(self, request):
        refresh_token = request.data.get('refresh')
        if refresh_token:
            try:
                refresh = RefreshToken(refresh_token)
                return Response({
                    'success': True,
                    'access': str(refresh.access_token)
                })
            except Exception:
                return Response({
                    'success': False,
                    'error': 'Invalid refresh token'
                }, status=status.HTTP_400_BAD_REQUEST)
        return Response({
            'success': False,
            'error': 'Refresh token required'
        }, status=status.HTTP_400_BAD_REQUEST)
    

    # Add these functions to your accounts/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from .models import User
from .utils import generate_otp, send_otp_email

def forgot_password_view(request):
    """Step 1: Request OTP for password reset"""
    if request.method == 'POST':
        email = request.POST.get('email')
        
        try:
            user = User.objects.get(email=email)
            
            # Generate OTP
            otp = generate_otp()
            user.otp_code = otp
            user.otp_created_at = timezone.now()
            user.otp_purpose = 'reset'
            user.save()
            
            # Store email in session
            request.session['reset_email'] = email
            
            # Send OTP email
            send_otp_email(user, otp, 'reset')
            
            messages.success(request, 'OTP sent to your email!')
            return redirect('verify-reset-otp')
            
        except User.DoesNotExist:
            messages.warning(request, 'No account found with this email')
            # POST par bhi render karna hai agar user nahi mila
            return render(request, 'accounts/forgot_password.html')
    
    # GET request - show the form
    return render(request, 'accounts/forgot_password.html')

def verify_reset_otp_view(request):
    """Step 2: Verify OTP"""
    reset_email = request.session.get('reset_email')
    
    if not reset_email:
        messages.error(request, 'Session expired. Please try again.')
        return redirect('forgot-password')
    
    if request.method == 'POST':
        otp_entered = request.POST.get('otp')
        
        try:
            user = User.objects.get(email=reset_email)
            
            if user.otp_code == otp_entered and user.otp_purpose == 'reset':
                time_diff = timezone.now() - user.otp_created_at
                if time_diff <= timedelta(minutes=10):
                    request.session['otp_verified'] = True
                    messages.success(request, 'OTP verified! Set new password.')
                    return redirect('set-new-password')
                else:
                    messages.error(request, 'OTP has expired. Request a new one.')
                    return render(request, 'accounts/verify_reset_otp.html', {'email': reset_email})
            else:
                messages.error(request, 'Invalid OTP. Please try again.')
                return render(request, 'accounts/verify_reset_otp.html', {'email': reset_email})
                
        except User.DoesNotExist:
            messages.error(request, 'User not found.')
            return redirect('forgot-password')
    
    # GET request - show OTP form
    return render(request, 'accounts/verify_reset_otp.html', {'email': reset_email})

def resend_reset_otp_view(request):
    """Resend OTP"""
    reset_email = request.session.get('reset_email')
    
    if not reset_email:
        messages.error(request, 'Session expired.')
        return redirect('forgot-password')
    
    try:
        user = User.objects.get(email=reset_email)
        otp = generate_otp()
        user.otp_code = otp
        user.otp_created_at = timezone.now()
        user.save()
        
        send_otp_email(user, otp, 'reset')
        messages.success(request, 'New OTP sent!')
        return redirect('verify-reset-otp')
        
    except User.DoesNotExist:
        messages.error(request, 'User not found.')
        return redirect('forgot-password')

def set_new_password_view(request):
    """Step 3: Set new password"""
    if not request.session.get('otp_verified'):
        messages.error(request, 'Please verify OTP first.')
        return redirect('forgot-password')
    
    reset_email = request.session.get('reset_email')
    
    if not reset_email:
        messages.error(request, 'Session expired.')
        return redirect('forgot-password')
    
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if new_password != confirm_password:
            messages.error(request, 'Passwords do not match')
            return render(request, 'accounts/set_new_password.html')
        elif len(new_password) < 8:
            messages.error(request, 'Password must be at least 8 characters')
            return render(request, 'accounts/set_new_password.html')
        else:
            try:
                user = User.objects.get(email=reset_email)
                user.set_password(new_password)
                user.otp_code = None
                user.otp_created_at = None
                user.otp_purpose = None
                user.save()
                
                # Clear session
                del request.session['reset_email']
                del request.session['otp_verified']
                
                messages.success(request, 'Password changed! Please login.')
                return redirect('login')
            except User.DoesNotExist:
                messages.error(request, 'User not found.')
                return redirect('forgot-password')
    
    # GET request - show password form
    return render(request, 'accounts/set_new_password.html')

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from blog.models import BlogPost, BlogCategory

@staff_member_required
def admin_blog_posts(request):
    posts = BlogPost.objects.all().order_by('-published_at')
    return render(request, 'admin/blog_posts.html', {'posts': posts})

@staff_member_required
def admin_blog_categories(request):
    categories = BlogCategory.objects.all()
    return render(request, 'admin/blog_categories.html', {'categories': categories})

@staff_member_required
def admin_blog_add(request):
    if request.method == 'POST':
        category = get_object_or_404(BlogCategory, id=request.POST.get('category'))
        
        BlogPost.objects.create(
            title=request.POST.get('title'),
            slug=request.POST.get('title').replace(' ', '-').lower(),
            author=request.user,
            category=category,
            abstract=request.POST.get('abstract'),
            introduction=request.POST.get('introduction', ''),
            literature_review=request.POST.get('literature_review', ''),
            methodology=request.POST.get('methodology', ''),
            analysis=request.POST.get('analysis', ''),
            findings=request.POST.get('findings', ''),
            conclusion=request.POST.get('conclusion', ''),
            references=request.POST.get('references', ''),
            keywords=request.POST.get('keywords', ''),
            published_at=timezone.now(),
            reading_time=int(request.POST.get('reading_time', 5)),
            status='published',
        )
        return redirect('/admin-panel/blog-posts/')
    
    categories = BlogCategory.objects.all()
    return render(request, 'admin/blog_add.html', {'categories': categories})

@staff_member_required
def admin_blog_edit(request, post_id):
    post = get_object_or_404(BlogPost, id=post_id)
    
    if request.method == 'POST':
        post.title = request.POST.get('title')
        post.abstract = request.POST.get('abstract')
        post.introduction = request.POST.get('introduction')
        post.keywords = request.POST.get('keywords')
        post.category_id = request.POST.get('category')
        post.save()
        return redirect('/admin-panel/blog-posts/')
    
    categories = BlogCategory.objects.all()
    return render(request, 'admin/blog_edit.html', {'post': post, 'categories': categories})

@staff_member_required
def admin_blog_delete(request, post_id):
    post = get_object_or_404(BlogPost, id=post_id)
    post.delete()
    return redirect('/admin-panel/blog-posts/')