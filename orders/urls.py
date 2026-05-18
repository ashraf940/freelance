from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('create/', views.create_order, name='create_order'),
    path('my-orders/', views.my_orders, name='my_orders'),
    path('<uuid:order_id>/', views.order_detail, name='order_detail'),
    path('<uuid:order_id>/payment/', views.payment_view, name='payment'),
    
    # API URLs
    path('api/orders/', views.OrderListAPIView.as_view(), name='api_order_list'),
    path('api/orders/create/', views.OrderCreateAPIView.as_view(), name='api_order_create'),
    path('api/orders/<uuid:id>/', views.OrderDetailAPIView.as_view(), name='api_order_detail'),
    path('api/orders/<uuid:id>/update/', views.OrderUpdateAPIView.as_view(), name='api_order_update'),
    path('api/orders/<uuid:order_id>/cancel/', views.CancelOrderAPIView.as_view(), name='api_order_cancel'),
]