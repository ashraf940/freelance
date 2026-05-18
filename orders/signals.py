from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order
from notifications.utils import create_notification

@receiver(post_save, sender=Order)
def order_notification_handler(sender, instance, created, **kwargs):
    """Send notifications when order status changes"""
    
    if created:
        # New order created - notify seller
        create_notification(
            user=instance.seller,
            notification_type='order_created',
            title='New Order Received! 🎉',
            message=f'You have received a new order for "{instance.gig.title}". Amount: ${instance.total_amount}',
            link=f'/orders/{instance.id}/'
        )
        
        # Notify buyer as well
        create_notification(
            user=instance.buyer,
            notification_type='order_created',
            title='Order Confirmed ✅',
            message=f'Your order #{instance.order_number} has been created successfully.',
            link=f'/orders/{instance.id}/'
        )
    
    else:
        # Order status changed
        old_status = getattr(instance, '_old_status', None)
        
        # Store old status before saving (in model)
        if hasattr(instance, 'track_status'):
            old_status = instance.track_status
        
        if old_status != instance.status:
            if instance.status == 'active':
                create_notification(
                    user=instance.buyer,
                    notification_type='order_active',
                    title='Order Active! 🚀',
                    message=f'Your order #{instance.order_number} is now active. Seller will start working.',
                    link=f'/orders/{instance.id}/'
                )
            
            elif instance.status == 'delivered':
                create_notification(
                    user=instance.buyer,
                    notification_type='order_delivered',
                    title='Order Delivered! 📦',
                    message=f'Order #{instance.order_number} has been delivered. Please check and confirm completion.',
                    link=f'/orders/{instance.id}/'
                )
            
            elif instance.status == 'completed':
                create_notification(
                    user=instance.seller,
                    notification_type='order_completed',
                    title='Order Completed! 🎯',
                    message=f'Order #{instance.order_number} has been completed successfully. Payment released.',
                    link=f'/orders/{instance.id}/'
                )
                
                # Also notify buyer about completion
                create_notification(
                    user=instance.buyer,
                    notification_type='order_completed',
                    title='Order Completed ✅',
                    message=f'Your order #{instance.order_number} is complete. Thank you for your business!',
                    link=f'/orders/{instance.id}/'
                )
            
            elif instance.status == 'cancelled':
                create_notification(
                    user=instance.buyer,
                    notification_type='order_cancelled',
                    title='Order Cancelled ❌',
                    message=f'Your order #{instance.order_number} has been cancelled.',
                    link=f'/orders/{instance.id}/'
                )
                create_notification(
                    user=instance.seller,
                    notification_type='order_cancelled',
                    title='Order Cancelled ❌',
                    message=f'Order #{instance.order_number} has been cancelled.',
                    link=f'/orders/{instance.id}/'
                )