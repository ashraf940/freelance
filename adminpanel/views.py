from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import timedelta
from django.core.paginator import Paginator
from django.http import JsonResponse
from .models import AdminLog, PlatformSettings, Announcement, WithdrawalRequest

# CORRECT IMPORTS - Apps are in root folder, NOT in apps folder
from accounts.models import User
from gigs.models import Gig, Category
from orders.models import Order
from reviews.models import Review

@staff_member_required
def dashboard(request):
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    # User Stats
    total_users = User.objects.count()
    total_freelancers = User.objects.filter(role='freelancer').count()
    total_clients = User.objects.filter(role='client').count()
    new_users_today = User.objects.filter(date_joined__date=today).count()
    new_users_week = User.objects.filter(date_joined__date__gte=week_ago).count()
    
    # Gig Stats
    total_gigs = Gig.objects.count()
    active_gigs = Gig.objects.filter(status='active').count()
    pending_gigs = Gig.objects.filter(status='pending').count()
    rejected_gigs = Gig.objects.filter(status='rejected').count()
    
    # Order Stats
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status='pending').count()
    active_orders = Order.objects.filter(status='active').count()
    completed_orders = Order.objects.filter(status='completed').count()
    cancelled_orders = Order.objects.filter(status='cancelled').count()
    new_orders_today = Order.objects.filter(created_at__date=today).count()
    
    # Revenue Stats
    total_revenue = Order.objects.filter(status='completed').aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    platform_commission = Order.objects.filter(status='completed').aggregate(Sum('service_fee'))['service_fee__sum'] or 0
    revenue_this_month = Order.objects.filter(
        status='completed',
        created_at__date__gte=month_ago
    ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    
    # Recent Activity
    recent_users = User.objects.all().order_by('-date_joined')[:10]
    recent_orders = Order.objects.all().order_by('-created_at')[:10]
    recent_gigs = Gig.objects.all().order_by('-created_at')[:10]
    recent_logs = AdminLog.objects.all().order_by('-created_at')[:10]
    
    # Chart Data (Last 7 days)
    chart_labels = []
    chart_orders = []
    chart_users = []
    
    for i in range(6, -1, -1):
        date = today - timedelta(days=i)
        chart_labels.append(date.strftime('%b %d'))
        chart_orders.append(Order.objects.filter(created_at__date=date).count())
        chart_users.append(User.objects.filter(date_joined__date=date).count())
    
    # Top Gigs
    top_gigs = Gig.objects.filter(status='active').order_by('-orders_count', '-rating')[:10]
    
    context = {
        'total_users': total_users,
        'total_freelancers': total_freelancers,
        'total_clients': total_clients,
        'new_users_today': new_users_today,
        'new_users_week': new_users_week,
        'total_gigs': total_gigs,
        'active_gigs': active_gigs,
        'pending_gigs': pending_gigs,
        'rejected_gigs': rejected_gigs,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'active_orders': active_orders,
        'completed_orders': completed_orders,
        'cancelled_orders': cancelled_orders,
        'new_orders_today': new_orders_today,
        'total_revenue': total_revenue,
        'platform_commission': platform_commission,
        'revenue_this_month': revenue_this_month,
        'recent_users': recent_users,
        'recent_orders': recent_orders,
        'recent_gigs': recent_gigs,
        'recent_logs': recent_logs,
        'chart_labels': chart_labels,
        'chart_orders': chart_orders,
        'chart_users': chart_users,
        'top_gigs': top_gigs,
    }
    return render(request, 'adminpanel/dashboard.html', context)

@staff_member_required
def user_list(request):
    users = User.objects.all().order_by('-date_joined')
    
    # Filters
    role = request.GET.get('role')
    if role:
        users = users.filter(role=role)
    
    status = request.GET.get('status')
    if status == 'active':
        users = users.filter(is_active=True, is_suspended=False)
    elif status == 'suspended':
        users = users.filter(is_suspended=True)
    elif status == 'verified':
        users = users.filter(email_verified=True)
    
    search = request.GET.get('search')
    if search:
        users = users.filter(
            Q(email__icontains=search) |
            Q(username__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search)
        )
    
    paginator = Paginator(users, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'users': page_obj,
        'total_users': users.count(),
        'role_filter': role,
        'status_filter': status,
    }
    return render(request, 'adminpanel/users.html', context)

@staff_member_required
def user_detail(request, user_id):
    user = get_object_or_404(User, id=user_id)
    
    # User stats
    gigs_count = Gig.objects.filter(freelancer=user).count()
    orders_as_buyer = Order.objects.filter(buyer=user).count()
    orders_as_seller = Order.objects.filter(seller=user).count()
    total_spent = Order.objects.filter(buyer=user, status='completed').aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    total_earned = Order.objects.filter(seller=user, status='completed').aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    
    # User's gigs
    user_gigs = Gig.objects.filter(freelancer=user).order_by('-created_at')[:10]
    
    # User's orders
    user_orders = Order.objects.filter(Q(buyer=user) | Q(seller=user)).order_by('-created_at')[:10]
    
    context = {
        'profile_user': user,
        'gigs_count': gigs_count,
        'orders_as_buyer': orders_as_buyer,
        'orders_as_seller': orders_as_seller,
        'total_spent': total_spent,
        'total_earned': total_earned,
        'user_gigs': user_gigs,
        'user_orders': user_orders,
    }
    return render(request, 'adminpanel/user_detail.html', context)

@staff_member_required
def user_suspend(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.is_suspended = not user.is_suspended
    user.suspension_reason = request.POST.get('reason', '')
    user.save()
    
    AdminLog.objects.create(
        admin=request.user,
        action='suspend',
        model_name='User',
        object_id=str(user.id),
        object_name=user.email,
        ip_address=get_client_ip(request)
    )
    
    status = 'suspended' if user.is_suspended else 'activated'
    messages.success(request, f'User {user.email} has been {status}!')
    return redirect('adminpanel:user_detail', user_id=user.id)

@staff_member_required
def user_verify(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.email_verified = True
    user.identity_verified = True
    user.save()
    
    AdminLog.objects.create(
        admin=request.user,
        action='verify',
        model_name='User',
        object_id=str(user.id),
        object_name=user.email,
        ip_address=get_client_ip(request)
    )
    
    messages.success(request, f'User {user.email} has been verified!')
    return redirect('adminpanel:user_detail', user_id=user.id)

@staff_member_required
def gig_list(request):
    gigs = Gig.objects.all().order_by('-created_at')
    
    # Filters
    status = request.GET.get('status')
    if status:
        gigs = gigs.filter(status=status)
    
    category = request.GET.get('category')
    if category:
        gigs = gigs.filter(category_id=category)
    
    search = request.GET.get('search')
    if search:
        gigs = gigs.filter(
            Q(title__icontains=search) |
            Q(freelancer__email__icontains=search)
        )
    
    paginator = Paginator(gigs, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    categories = Category.objects.all()
    
    context = {
        'gigs': page_obj,
        'total_gigs': gigs.count(),
        'categories': categories,
        'status_filter': status,
    }
    return render(request, 'adminpanel/gigs.html', context)

@staff_member_required
def gig_detail(request, gig_id):
    gig = get_object_or_404(Gig, id=gig_id)
    
    # Gig analytics
    orders = Order.objects.filter(gig=gig)
    total_orders = orders.count()
    completed_orders = orders.filter(status='completed').count()
    total_revenue = orders.filter(status='completed').aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    
    # Reviews
    reviews = Review.objects.filter(gig=gig)
    
    context = {
        'gig': gig,
        'total_orders': total_orders,
        'completed_orders': completed_orders,
        'total_revenue': total_revenue,
        'reviews': reviews,
    }
    return render(request, 'adminpanel/gig_detail.html', context)

@staff_member_required
def gig_approve(request, gig_id):
    gig = get_object_or_404(Gig, id=gig_id)
    gig.status = 'active'
    gig.save()
    
    AdminLog.objects.create(
        admin=request.user,
        action='approve',
        model_name='Gig',
        object_id=str(gig.id),
        object_name=gig.title,
        ip_address=get_client_ip(request)
    )
    
    messages.success(request, f'Gig "{gig.title}" approved!')
    return redirect('adminpanel:gigs')

@staff_member_required
def gig_reject(request, gig_id):
    gig = get_object_or_404(Gig, id=gig_id)
    reason = request.POST.get('reason', '')
    gig.status = 'rejected'
    gig.rejection_reason = reason
    gig.save()
    
    AdminLog.objects.create(
        admin=request.user,
        action='reject',
        model_name='Gig',
        object_id=str(gig.id),
        object_name=gig.title,
        ip_address=get_client_ip(request)
    )
    
    messages.success(request, f'Gig "{gig.title}" rejected!')
    return redirect('adminpanel:gigs')

@staff_member_required
def gig_feature(request, gig_id):
    gig = get_object_or_404(Gig, id=gig_id)
    gig.is_featured = not gig.is_featured
    gig.save()
    
    status = 'featured' if gig.is_featured else 'unfeatured'
    messages.success(request, f'Gig "{gig.title}" has been {status}!')
    return redirect('adminpanel:gigs')

@staff_member_required
def order_list(request):
    orders = Order.objects.all().order_by('-created_at')
    
    # Filters
    status = request.GET.get('status')
    if status:
        orders = orders.filter(status=status)
    
    search = request.GET.get('search')
    if search:
        orders = orders.filter(
            Q(order_number__icontains=search) |
            Q(buyer__email__icontains=search) |
            Q(seller__email__icontains=search)
        )
    
    paginator = Paginator(orders, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'orders': page_obj,
        'total_orders': orders.count(),
        'status_filter': status,
    }
    return render(request, 'adminpanel/orders.html', context)

@staff_member_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'adminpanel/order_detail.html', {'order': order})

@staff_member_required
def resolve_dispute(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'refund_buyer':
            order.status = 'cancelled'
            order.save()
            messages.success(request, 'Refund processed to buyer!')
        elif action == 'release_payment':
            order.status = 'completed'
            order.save()
            messages.success(request, 'Payment released to seller!')
        
        return redirect('adminpanel:order_detail', order_id=order.id)
    
    return render(request, 'adminpanel/resolve_dispute.html', {'order': order})

@staff_member_required
def withdrawal_list(request):
    withdrawals = WithdrawalRequest.objects.all().order_by('-created_at')
    
    status = request.GET.get('status')
    if status:
        withdrawals = withdrawals.filter(status=status)
    
    paginator = Paginator(withdrawals, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'withdrawals': page_obj,
        'pending_count': WithdrawalRequest.objects.filter(status='pending').count(),
        'approved_count': WithdrawalRequest.objects.filter(status='approved').count(),
        'completed_count': WithdrawalRequest.objects.filter(status='completed').count(),
    }
    return render(request, 'adminpanel/withdrawals.html', context)

@staff_member_required
def approve_withdrawal(request, wd_id):
    withdrawal = get_object_or_404(WithdrawalRequest, id=wd_id)
    withdrawal.status = 'approved'
    withdrawal.processed_by = request.user
    withdrawal.processed_at = timezone.now()
    withdrawal.save()
    
    messages.success(request, f'Withdrawal of ${withdrawal.amount} approved!')
    return redirect('adminpanel:withdrawals')

@staff_member_required
def review_list(request):
    reviews = Review.objects.all().order_by('-created_at')
    
    search = request.GET.get('search')
    if search:
        reviews = reviews.filter(
            Q(comment__icontains=search) |
            Q(reviewer__email__icontains=search) |
            Q(freelancer__email__icontains=search)
        )
    
    paginator = Paginator(reviews, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'reviews': page_obj,
        'total_reviews': reviews.count(),
    }
    return render(request, 'adminpanel/reviews.html', context)

@staff_member_required
def review_delete(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    review.delete()
    
    messages.success(request, 'Review deleted successfully!')
    return redirect('adminpanel:reviews')

@staff_member_required
def settings(request):
    settings_obj, created = PlatformSettings.objects.get_or_create(id=1)
    
    if request.method == 'POST':
        settings_obj.site_name = request.POST.get('site_name')
        settings_obj.commission_rate = request.POST.get('commission_rate')
        settings_obj.min_withdrawal = request.POST.get('min_withdrawal')
        settings_obj.contact_email = request.POST.get('contact_email')
        settings_obj.support_phone = request.POST.get('support_phone')
        
        if request.FILES.get('site_logo'):
            settings_obj.site_logo = request.FILES.get('site_logo')
        
        settings_obj.save()
        messages.success(request, 'Settings updated successfully!')
        return redirect('adminpanel:settings')
    
    context = {
        'settings': settings_obj,
    }
    return render(request, 'adminpanel/settings.html', context)

@staff_member_required
def announcements(request):
    announcements = Announcement.objects.all().order_by('-created_at')
    
    if request.method == 'POST':
        title = request.POST.get('title')
        message = request.POST.get('message')
        announcement_type = request.POST.get('type', 'info')
        
        Announcement.objects.create(
            title=title,
            message=message,
            announcement_type=announcement_type,
            created_by=request.user
        )
        messages.success(request, 'Announcement created!')
        return redirect('adminpanel:announcements')
    
    context = {
        'announcements': announcements,
    }
    return render(request, 'adminpanel/announcements.html', context)

@staff_member_required
def announcement_delete(request, ann_id):
    announcement = get_object_or_404(Announcement, id=ann_id)
    announcement.delete()
    messages.success(request, 'Announcement deleted!')
    return redirect('adminpanel:announcements')

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip