from .models import Notification

def create_notification(user, notification_type, title, message, link=''):
    """Create notification for user"""
    Notification.objects.create(
        user=user,
        notification_type=notification_type,
        title=title,
        message=message,
        link=link
    )