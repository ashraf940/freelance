from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q

from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema

from .models import Order
from .serializers import (
    OrderSerializer, OrderCreateSerializer, 
    OrderUpdateSerializer, OrderDetailSerializer
)
from gigs.models import Gig


# ================= FRONTEND VIEWS =================

@login_required
def create_order(request):
    if request.method == 'POST':
        gig_id = request.POST.get('gig_id')
        gig = get_object_or_404(Gig, id=gig_id, status='active')

        order = Order.objects.create(
            buyer=request.user,
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

        messages.success(request, f'Order #{order.order_number} created!')
        return redirect('orders:payment', order_id=order.id)

    return redirect('gigs:gig_list')


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if order.buyer != request.user and order.seller != request.user:
        messages.error(request, 'No permission')
        return redirect('orders:my_orders')

    return render(request, 'orders/order_detail.html', {'order': order})


@login_required
def my_orders(request):
    if request.user.role == 'freelancer':
        orders_as_seller = Order.objects.filter(seller=request.user)
        orders_as_buyer = Order.objects.filter(buyer=request.user)
    else:
        orders_as_seller = Order.objects.none()
        orders_as_buyer = Order.objects.filter(buyer=request.user)

    return render(request, 'orders/my_orders.html', {
        'orders_as_buyer': orders_as_buyer,
        'orders_as_seller': orders_as_seller,
    })


@login_required
def payment_view(request, order_id):
    order = get_object_or_404(Order, id=order_id, buyer=request.user, status='pending')

    if request.method == 'POST':
        order.status = 'active'
        order.save()
        messages.success(request, 'Payment successful!')
        return redirect('orders:order_detail', order_id=order.id)

    return render(request, 'orders/payment.html', {'order': order})


# ================= API VIEWS =================

class OrderListAPIView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Order.objects.filter(Q(buyer=user) | Q(seller=user))


class OrderDetailAPIView(generics.RetrieveAPIView):
    serializer_class = OrderDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        user = self.request.user
        return Order.objects.filter(Q(buyer=user) | Q(seller=user))


class OrderCreateAPIView(generics.CreateAPIView):
    serializer_class = OrderCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        request_body=OrderCreateSerializer,
        responses={201: OrderSerializer()}
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

class OrderUpdateAPIView(generics.UpdateAPIView):
    serializer_class = OrderUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        # Buyer and seller both can update (buyer completes, seller delivers)
        return Order.objects.filter(Q(seller=self.request.user) | Q(buyer=self.request.user))
    
    def perform_update(self, serializer):
        order = self.get_object()
        old_status = order.status
        new_status = serializer.validated_data.get('status', old_status)
        
        print(f"Order #{order.order_number}: {old_status} -> {new_status}")
        
        # If order is being marked as delivered by seller
        if old_status == 'active' and new_status == 'delivered':
            print(f"Order {order.order_number} marked as delivered")
        
        # If order is being completed by buyer
        if old_status == 'delivered' and new_status == 'completed':
            gig = order.gig
            gig.orders_count += 1
            gig.save()
            print(f"Gig {gig.title} orders_count updated to {gig.orders_count}")
        
        serializer.save()

class CancelOrderAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id)

            if order.buyer != request.user:
                return Response({'error': 'Not authorized'}, status=403)

            if order.status not in ['pending', 'active']:
                return Response({'error': 'Cannot cancel'}, status=400)

            order.status = 'cancelled'
            order.save()

            return Response({'message': 'Cancelled'})
        except Order.DoesNotExist:
            return Response({'error': 'Not found'}, status=404)