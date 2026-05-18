from rest_framework import serializers
from .models import Order
from gigs.serializers import GigSerializer
from accounts.serializers import UserSerializer

class OrderSerializer(serializers.ModelSerializer):
    buyer_name = serializers.CharField(source='buyer.get_full_name', read_only=True)
    buyer_email = serializers.CharField(source='buyer.email', read_only=True)
    seller_name = serializers.CharField(source='seller.get_full_name', read_only=True)
    seller_email = serializers.CharField(source='seller.email', read_only=True)
    gig_title = serializers.CharField(source='gig.title', read_only=True)
    gig_slug = serializers.CharField(source='gig.slug', read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'buyer_name', 'buyer_email',
            'seller_name', 'seller_email', 'gig_title', 'gig_slug',
            'title', 'description', 'amount', 'service_fee',
            'total_amount', 'delivery_days', 'status',
            'created_at', 'updated_at', 'delivered_at'
        ]
        read_only_fields = ['id', 'order_number', 'created_at', 'updated_at']

class OrderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['gig', 'requirements']
    
    def validate_gig(self, value):
        if value.status != 'active':
            raise serializers.ValidationError("This gig is not available")
        return value
    
    def create(self, validated_data):
        gig = validated_data['gig']
        user = self.context['request'].user
        
        order = Order.objects.create(
            buyer=user,
            seller=gig.freelancer,
            gig=gig,
            title=gig.title,
            description=gig.description,
            amount=gig.price,
            service_fee=round(float(gig.price) * 0.10, 2),
            total_amount=round(float(gig.price) * 1.10, 2),
            delivery_days=gig.delivery_days,
            status='pending'
        )
        return order

class OrderUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['status', 'cancellation_reason']
    
    def validate_status(self, value):
        if value == 'cancelled':
            # Add cancellation validation
            pass
        return value

class OrderStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['status', 'delivered_at']
        read_only_fields = ['delivered_at']

class OrderDetailSerializer(serializers.ModelSerializer):
    buyer = UserSerializer(read_only=True)
    seller = UserSerializer(read_only=True)
    gig = GigSerializer(read_only=True)
    
    class Meta:
        model = Order
        fields = '__all__'