from django.urls import path
from . import views

app_name = 'adminpanel'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    
    # User Management
    path('users/', views.user_list, name='users'),
    path('users/<uuid:user_id>/', views.user_detail, name='user_detail'),
    path('users/<uuid:user_id>/suspend/', views.user_suspend, name='user_suspend'),
    path('users/<uuid:user_id>/verify/', views.user_verify, name='user_verify'),
    
    # Gig Management
    path('gigs/', views.gig_list, name='gigs'),
    path('gigs/<uuid:gig_id>/', views.gig_detail, name='gig_detail'),
    path('gigs/<uuid:gig_id>/approve/', views.gig_approve, name='gig_approve'),
    path('gigs/<uuid:gig_id>/reject/', views.gig_reject, name='gig_reject'),
    path('gigs/<uuid:gig_id>/feature/', views.gig_feature, name='gig_feature'),
    
    # Order Management
    path('orders/', views.order_list, name='orders'),
    path('orders/<uuid:order_id>/', views.order_detail, name='order_detail'),
    path('orders/<uuid:order_id>/dispute/', views.resolve_dispute, name='resolve_dispute'),
    
    # Payment Management
    path('withdrawals/', views.withdrawal_list, name='withdrawals'),
    path('withdrawals/<uuid:wd_id>/approve/', views.approve_withdrawal, name='approve_withdrawal'),
    
    # Review Management
    path('reviews/', views.review_list, name='reviews'),
    path('reviews/<uuid:review_id>/delete/', views.review_delete, name='review_delete'),
    
    # Settings
    path('settings/', views.settings, name='settings'),
    path('announcements/', views.announcements, name='announcements'),
    path('announcements/<uuid:ann_id>/delete/', views.announcement_delete, name='announcement_delete'),
]