from django.db import models
from django.conf import settings
from gigs.models import Gig
import uuid

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('delivered', 'Delivered'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('disputed', 'Disputed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_number = models.CharField(max_length=20, unique=True, blank=True)
    
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders_as_buyer')
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders_as_seller')
    gig = models.ForeignKey(Gig, on_delete=models.CASCADE, related_name='orders')
    
    # Order Details
    title = models.CharField(max_length=200)
    description = models.TextField()
    requirements = models.JSONField(default=dict)
    
    # Pricing
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    service_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Delivery
    delivery_days = models.IntegerField()
    delivered_at = models.DateTimeField(null=True, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    cancellation_reason = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.order_number} - {self.title}"
    

def save(self, *args, **kwargs):
    # Track old status for signal
    if self.pk:
        self.track_status = Order.objects.get(pk=self.pk).status
    else:
        self.track_status = None
    
    if not self.order_number:
        self.order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"
    super().save(*args, **kwargs)