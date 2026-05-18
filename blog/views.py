from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import BlogPost, BlogCategory, BlogComment

def blog_list(request):
    posts = BlogPost.objects.filter(status='published').select_related('author', 'category')
    
    # Search
    search_query = request.GET.get('q')
    if search_query:
        posts = posts.filter(
            Q(title__icontains=search_query) |
            Q(abstract__icontains=search_query) |
            Q(keywords__icontains=search_query) |
            Q(tags__icontains=search_query)
        )
    
    # Category filter
    category_slug = request.GET.get('category')
    if category_slug:
        posts = posts.filter(category__slug=category_slug)
    
    # Pagination
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    categories = BlogCategory.objects.filter(is_active=True).annotate(
        post_count=Count('posts', filter=Q(posts__status='published'))
    )
    
    context = {
        'posts': page_obj,
        'categories': categories,
        'search_query': search_query,
    }
    return render(request, 'blog/list.html', context)

def blog_detail(request, slug):
    post = get_object_or_404(BlogPost, slug=slug, status='published')
    post.increment_views()
    
    # Related posts
    related_posts = BlogPost.objects.filter(
        category=post.category, 
        status='published'
    ).exclude(id=post.id)[:5]
    
    context = {
        'post': post,
        'related_posts': related_posts,
    }
    return render(request, 'blog/detail.html', context)

@login_required
def add_comment(request, post_id):
    post = get_object_or_404(BlogPost, id=post_id, status='published')
    
    if request.method == 'POST':
        comment_text = request.POST.get('comment')
        if comment_text:
            BlogComment.objects.create(
                post=post,
                user=request.user,
                comment=comment_text,
                is_approved=False
            )
            messages.success(request, 'Your comment has been submitted for moderation.')
        else:
            messages.error(request, 'Please enter a comment.')
    
    return redirect('blog:detail', slug=post.slug)

def blog_category(request, slug):
    category = get_object_or_404(BlogCategory, slug=slug, is_active=True)
    posts = BlogPost.objects.filter(category=category, status='published')
    
    context = {
        'category': category,
        'posts': posts,
    }
    return render(request, 'blog/category.html', context)


from django.shortcuts import redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from .models import BlogPost, BlogCategory
from accounts.models import User

@staff_member_required
def quick_add_blog(request):
    user = User.objects.first()
    category = BlogCategory.objects.first()
    
    if not category:
        category = BlogCategory.objects.create(
            name="Technology",
            slug="technology"
        )
    
    blog = BlogPost.objects.create(
        title="Test Blog",
        slug="test-blog",
        author=user,
        category=category,
        abstract="This is a test blog post",
        introduction="<p>Test content here</p>",
        keywords="test, blog",
        published_at=timezone.now(),
        reading_time=5,
        status='published',
    )
    
    return redirect('/blog/')