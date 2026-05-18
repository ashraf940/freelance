from django.db.models.signals import post_save
from django.dispatch import receiver
from orders.models import Order
from reviews.models import Review
from .utils import create_notification

@receiver(post_save, sender=Order)
def order_notification(sender, instance, created, **kwargs):
    if created:
        # New order created - notify seller
        create_notification(
            user=instance.seller,
            notification_type='order_created',
            title='New Order Received!',
            message=f'You have received a new order for "{instance.gig.title}". Amount: ${instance.total_amount}',
            link=f'/orders/{instance.id}/'
        )
        
        # Notify buyer as well
        create_notification(
            user=instance.buyer,
            notification_type='order_created',
            title='Order Created',
            message=f'Your order #{instance.order_number} has been created successfully.',
            link=f'/orders/{instance.id}/'
        )
    
    else:
        # Order status changed
        old_status = getattr(instance, '_old_status', None)
        if old_status != instance.status:
            if instance.status == 'active':
                create_notification(
                    user=instance.buyer,
                    notification_type='order_active',
                    title='Order Active',
                    message=f'Your order #{instance.order_number} is now active. Seller will start working.',
                    link=f'/orders/{instance.id}/'
                )
            
            elif instance.status == 'delivered':
                create_notification(
                    user=instance.buyer,
                    notification_type='order_delivered',
                    title='Order Delivered!',
                    message=f'Order #{instance.order_number} has been delivered. Please review and complete.',
                    link=f'/orders/{instance.id}/'
                )
            
            elif instance.status == 'completed':
                create_notification(
                    user=instance.seller,
                    notification_type='order_completed',
                    title='Order Completed!',
                    message=f'Order #{instance.order_number} has been completed successfully.',
                    link=f'/orders/{instance.id}/'
                )
            
            elif instance.status == 'cancelled':
                create_notification(
                    user=instance.buyer,
                    notification_type='order_cancelled',
                    title='Order Cancelled',
                    message=f'Your order #{instance.order_number} has been cancelled.',
                    link=f'/orders/{instance.id}/'
                )
                create_notification(
                    user=instance.seller,
                    notification_type='order_cancelled',
                    title='Order Cancelled',
                    message=f'Order #{instance.order_number} has been cancelled.',
                    link=f'/orders/{instance.id}/'
                )

@receiver(post_save, sender=Review)
def review_notification(sender, instance, created, **kwargs):
    if created:
        create_notification(
            user=instance.freelancer,
            notification_type='review_received',
            title='New Review Received!',
            message=f'{instance.reviewer.get_full_name()} rated your gig {instance.rating} stars: "{instance.comment[:50]}"',
            link=f'/gigs/{instance.gig.slug}/'
        )