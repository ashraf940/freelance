from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Review
from orders.models import Order

@login_required
def add_review(request, order_id):
    order = get_object_or_404(Order, id=order_id, buyer=request.user, status='completed')
    
    # Check if review already exists
    if Review.objects.filter(order=order).exists():
        messages.error(request, 'You have already reviewed this order')
        return redirect('orders:order_detail', order_id=order.id)
    
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment', '')
        
        Review.objects.create(
            order=order,
            gig=order.gig,
            reviewer=request.user,
            freelancer=order.seller,
            rating=rating,
            comment=comment
        )
        
        # Update gig rating
        order.gig.update_rating()
        
        messages.success(request, 'Thank you for your review!')
        return redirect('orders:order_detail', order_id=order.id)
    
    return render(request, 'reviews/add_review.html', {'order': order})

@login_required
def edit_review(request, review_id):
    review = get_object_or_404(Review, id=review_id, reviewer=request.user)
    
    if request.method == 'POST':
        review.rating = request.POST.get('rating')
        review.comment = request.POST.get('comment', '')
        review.save()
        messages.success(request, 'Review updated successfully')
        return redirect('orders:order_detail', order_id=review.order.id)
    
    return render(request, 'reviews/edit_review.html', {'review': review})