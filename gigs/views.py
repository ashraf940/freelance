from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Avg, Count, Sum
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from .models import Gig, Category, SubCategory, SavedGig
from .forms import GigCreateForm, GigPackageForm, GigRequirementForm, GigFaqForm
from .filters import GigFilter

# FIX 1: @cache_page hata diya — dynamic filters ke saath conflict hota tha
def gig_list(request):
    """List all active gigs with filters"""
    gigs = Gig.objects.filter(status='active').select_related('freelancer', 'category')
    
    gig_filter = GigFilter(request.GET, queryset=gigs)
    gigs = gig_filter.qs
    
    paginator = Paginator(gigs, 24)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    categories = Category.objects.filter(is_active=True).annotate(
        gig_count=Count('gigs', filter=Q(gigs__status='active'))
    )
    
    context = {
        'gigs': page_obj,        # ← YEH IMPORTANT HAI
        'filter': gig_filter,
        'categories': categories,
        'total_gigs': gigs.count(),
    }
    return render(request, 'gigs/gig_list.html', context)


def gig_detail(request, slug):
    """Gig detail page"""
    gig = get_object_or_404(Gig, slug=slug, status='active')
    gig.increment_views()
    
    related_gigs = Gig.objects.filter(
        category=gig.category,
        status='active'
    ).exclude(id=gig.id)[:6]
    
    is_saved = False
    if request.user.is_authenticated:
        is_saved = SavedGig.objects.filter(user=request.user, gig=gig).exists()
    
    context = {
        'gig': gig,
        'related_gigs': related_gigs,
        'is_saved': is_saved,
        'packages': gig.packages.filter(is_active=True),
        'faqs': gig.faqs.all(),
    }
    return render(request, 'gigs/gig_detail.html', context)


@login_required
def create_gig(request):
    """Create new gig"""
    from .models import Category
    
    if not request.user.is_freelancer:
        messages.error(request, 'Only freelancers can create gigs')
        return redirect('gigs:gig_list')
    
    categories = Category.objects.filter(is_active=True)
    
    # DEBUG: Check if categories exist
    print(f"Categories count: {categories.count()}")
    for cat in categories:
        print(f"Category: {cat.name}")
    
    if request.method == 'POST':
        form = GigCreateForm(request.POST, request.FILES)
        if form.is_valid():
            gig = form.save(commit=False)
            gig.freelancer = request.user
            gig.status = 'active'
            gig.save()
            messages.success(request, 'Gig created successfully!')
            return redirect('gigs:my_gigs')
        else:
            # Print form errors to terminal
            print("Form errors:", form.errors)
            messages.error(request, f'Form errors: {form.errors}')
    else:
        form = GigCreateForm()
    
    context = {
        'form': form,
        'categories': categories,
    }
    return render(request, 'gigs/gig_create.html', context)


@login_required
def edit_gig(request, gig_id):
    """Edit existing gig"""
    gig = get_object_or_404(Gig, id=gig_id, freelancer=request.user)
    
    if request.method == 'POST':
        form = GigCreateForm(request.POST, request.FILES, instance=gig)
        if form.is_valid():
            form.save()
            messages.success(request, 'Gig updated successfully')
            return redirect('gigs:my_gigs')
    else:
        form = GigCreateForm(instance=gig)
    
    return render(request, 'gigs/gig_edit.html', {'form': form, 'gig': gig})


@login_required
def my_gigs(request):
    """List freelancer's gigs"""
    gigs = Gig.objects.filter(freelancer=request.user).order_by('-created_at')
    
    # FIX 2: models.Sum -> direct Sum (already imported above)
    # FIX 3: total_revenue galat tha — Gig pe 'completed' filter nahi hota
    stats = {
        'total': gigs.count(),
        'active': gigs.filter(status='active').count(),
        'pending': gigs.filter(status='pending').count(),
        'total_orders': gigs.aggregate(total=Sum('orders_count'))['total'] or 0,
        'total_revenue': 0,  # Order model se calculate karo apne project mein
    }
    
    context = {
        'gigs': gigs,
        'stats': stats,
    }
    return render(request, 'gigs/my_gigs.html', context)


@login_required
@require_http_methods(['POST'])
def delete_gig(request, gig_id):
    """Delete gig (soft delete)"""
    gig = get_object_or_404(Gig, id=gig_id, freelancer=request.user)
    
    if gig.orders_count > 0:
        messages.error(request, 'Cannot delete gig with existing orders')
    else:
        gig.status = 'deleted'
        gig.save()
        messages.success(request, 'Gig deleted successfully')
    
    return redirect('gigs:my_gigs')


@login_required
@require_http_methods(['POST'])
def toggle_gig_status(request, gig_id):
    """Pause/Activate gig"""
    gig = get_object_or_404(Gig, id=gig_id, freelancer=request.user)
    
    if gig.status == 'active':
        gig.status = 'paused'
        messages.success(request, 'Gig paused successfully')
    elif gig.status == 'paused':
        gig.status = 'active'
        messages.success(request, 'Gig activated successfully')
    
    gig.save()
    return redirect('gigs:my_gigs')


@login_required
def save_gig(request, gig_id):
    """Save/unsave gig to favorites"""
    gig = get_object_or_404(Gig, id=gig_id, status='active')
    
    saved, created = SavedGig.objects.get_or_create(user=request.user, gig=gig)
    
    if created:
        message = 'Gig saved to favorites'
        saved_status = True
    else:
        saved.delete()
        message = 'Gig removed from favorites'
        saved_status = False
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'saved': saved_status, 'message': message})
    
    return redirect('gigs:gig_detail', slug=gig.slug)


@login_required
def saved_gigs(request):
    """List user's saved gigs"""
    saved = SavedGig.objects.filter(user=request.user).select_related('gig')
    return render(request, 'gigs/saved_gigs.html', {'saved_gigs': saved})


def category_gigs(request, slug):
    """Gigs by category"""
    category = get_object_or_404(Category, slug=slug, is_active=True)
    gigs = Gig.objects.filter(category=category, status='active')
    subcategories = SubCategory.objects.filter(category=category, is_active=True)
    
    context = {
        'category': category,
        'gigs': gigs,
        'subcategories': subcategories,
    }
    return render(request, 'gigs/category_gigs.html', context)


@login_required
def gig_analytics(request, gig_id):
    """Analytics for specific gig"""
    # FIX 4: 'Grid' typo tha — 'Gig' hai
    gig = get_object_or_404(Gig, id=gig_id, freelancer=request.user)
    
    # FIX 5: Order import add kiya
    try:
        from orders.models import Order  # apne app ka naam match karo
        orders = Order.objects.filter(gig=gig)
        total_orders = orders.count()
        completed_orders = orders.filter(status='completed').count()
        total_revenue = orders.filter(status='completed').aggregate(
            total=Sum('amount')
        )['total'] or 0
    except ImportError:
        # Agar orders app abhi nahi bana toh fallback
        total_orders = gig.orders_count
        completed_orders = 0
        total_revenue = 0
    
    context = {
        'gig': gig,
        'total_orders': total_orders,
        'completed_orders': completed_orders,
        'total_revenue': total_revenue,
        'average_rating': gig.rating,
    }
    return render(request, 'gigs/gig_analytics.html', context)


# from django.http import HttpResponse

# def gig_list(request):
#     return HttpResponse("<h1>Gigs Page Working!</h1><p>Your gigs will appear here.</p>")


from django.shortcuts import render
from .models import Gig, Category

def gig_list(request):
    from django.core.paginator import Paginator
    from .models import Gig, Category
    
    gigs = Gig.objects.filter(status='active')
    categories = Category.objects.filter(is_active=True)
    
    # Search and filters
    category_id = request.GET.get('category')
    if category_id:
        gigs = gigs.filter(category_id=category_id)
    
    min_price = request.GET.get('min_price')
    if min_price:
        gigs = gigs.filter(price__gte=min_price)
    
    max_price = request.GET.get('max_price')
    if max_price:
        gigs = gigs.filter(price__lte=max_price)
    
    # Pagination
    paginator = Paginator(gigs, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'gigs': page_obj,
        'categories': categories,
        'total_gigs': gigs.count(),
    }
    return render(request, 'gigs/gig_list.html', context)


def gig_list(request):
    """List all active gigs with filters"""
    from django.core.paginator import Paginator
    from django.db.models import Q, Count
    from .models import Gig, Category
    
    # Get all active gigs
    gigs = Gig.objects.filter(status='active').select_related('freelancer', 'category')
    
    # Search filter
    search_query = request.GET.get('q')
    if search_query:
        gigs = gigs.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(short_description__icontains=search_query) |
            Q(tags__icontains=search_query)
        )
    
    # Category filter
    category_id = request.GET.get('category')
    if category_id:
        gigs = gigs.filter(category_id=category_id)
    
    # Price range filter
    min_price = request.GET.get('min_price')
    if min_price:
        gigs = gigs.filter(price__gte=min_price)
    
    max_price = request.GET.get('max_price')
    if max_price:
        gigs = gigs.filter(price__lte=max_price)
    
    # Delivery days filter
    min_delivery = request.GET.get('min_delivery')
    if min_delivery:
        gigs = gigs.filter(delivery_days__gte=min_delivery)
    
    max_delivery = request.GET.get('max_delivery')
    if max_delivery:
        gigs = gigs.filter(delivery_days__lte=max_delivery)
    
    # Rating filter
    min_rating = request.GET.get('min_rating')
    if min_rating:
        gigs = gigs.filter(rating__gte=min_rating)
    
    # Sorting
    ordering = request.GET.get('ordering')
    if ordering:
        gigs = gigs.order_by(ordering)
    else:
        gigs = gigs.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(gigs, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Categories for filter
    categories = Category.objects.filter(is_active=True).annotate(
        gig_count=Count('gigs', filter=Q(gigs__status='active'))
    )
    
    context = {
        'gigs': page_obj,
        'categories': categories,
        'total_gigs': gigs.count(),
    }
    
    # IMPORTANT: Return statement hona chahiye
    return render(request, 'gigs/gig_list.html', context)