import random
import threading
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

def generate_otp():
    """Generate 6-digit OTP"""
    return str(random.randint(100000, 999999))

class EmailThread(threading.Thread):
    """Send email in background thread"""
    def __init__(self, subject, html_message, recipient_list):
        self.subject = subject
        self.html_message = html_message
        self.recipient_list = recipient_list
        threading.Thread.__init__(self)
    
    def run(self):
        try:
            send_mail(
                subject=self.subject,
                message=strip_tags(self.html_message),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=self.recipient_list,
                html_message=self.html_message,
                fail_silently=False,
            )
        except Exception as e:
            print(f"Email error: {e}")

def send_otp_email(user, otp, email_type='reset'):
    """Send OTP email to user"""
    if email_type == 'reset':
        subject = 'Password Reset OTP - Freelance Platform'
        template = 'emails/reset_password_otp.html'
    else:
        subject = 'Verify Your Email - Freelance Platform'
        template = 'emails/verify_otp.html'
    
    html_message = render_to_string(template, {
        'user': user,
        'otp': otp,
        'site_name': 'Freelance Platform',
        'year': '2024'
    })
    
    # Send email in background thread
    EmailThread(subject, html_message, [user.email]).start()
    return True