from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid

User = get_user_model()

class Category(models.Model):
    """Gig Categories"""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=50, help_text="FontAwesome icon class")
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', null=True, blank=True)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', 'name']
        verbose_name_plural = 'Categories'
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
    # @property
    # def gig_count(self):
    #     return self.gigs.filter(status='active').count()

class SubCategory(models.Model):
    """Sub Categories"""
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')
    name = models.CharField(max_length=100)
    slug = models.SlugField()
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ('category', 'slug')
        ordering = ['name']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.category.name} - {self.name}"

class Gig(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending', 'Pending Approval'),
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('rejected', 'Rejected'),
        ('deleted', 'Deleted'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    freelancer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='gigs')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='gigs')
    sub_category = models.ForeignKey(SubCategory, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Basic Info
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    short_description = models.CharField(max_length=300, blank=True)
    
    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(5)])
    
    # Delivery
    delivery_days = models.IntegerField(default=3, validators=[MinValueValidator(1), MaxValueValidator(90)])
    revisions = models.IntegerField(default=1, validators=[MinValueValidator(0), MaxValueValidator(10)])
    
    # Media
    featured_image = models.ImageField(upload_to='gigs/featured/')
    gallery_images = models.JSONField(default=list, blank=True)
    video_url = models.URLField(blank=True, help_text="YouTube or Vimeo URL")
    
    # Requirements
    requirements = models.JSONField(default=list, blank=True, help_text="List of questions for buyer")
    
    # SEO
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(max_length=500, blank=True)
    tags = models.CharField(max_length=500, blank=True, help_text="Comma separated tags")
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    rejection_reason = models.TextField(blank=True)
    is_featured = models.BooleanField(default=False)
    
    # Statistics
    views = models.IntegerField(default=0)
    clicks = models.IntegerField(default=0)
    orders_count = models.IntegerField(default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    total_reviews = models.IntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-is_featured', '-rating', 'price']
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['category', 'status']),
            models.Index(fields=['freelancer', 'status']),
            models.Index(fields=['slug']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Gig.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title
    
    def update_rating(self):
        from reviews.models import Review
        from django.db.models import Avg
        
        reviews = Review.objects.filter(gig=self, is_approved=True)
        if reviews.exists():
            avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
            self.rating = round(avg_rating, 2)
            self.total_reviews = reviews.count()
            self.save(update_fields=['rating', 'total_reviews'])
            print(f"Updated: {self.title} - Rating: {self.rating}, Reviews: {self.total_reviews}")
        else:
            self.rating = 0
            self.total_reviews = 0
            self.save(update_fields=['rating', 'total_reviews'])
    
    def increment_views(self):
        self.views += 1
        self.save(update_fields=['views'])
    
    @property
    def is_available(self):
        return self.status == 'active'
    
    @property
    def average_rating(self):
        return round(self.rating, 1)

class GigPackage(models.Model):
    """Pricing packages for gig"""
    PACKAGE_CHOICES = [
        ('basic', 'Basic'),
        ('standard', 'Standard'),
        ('premium', 'Premium'),
    ]
    
    gig = models.ForeignKey(Gig, on_delete=models.CASCADE, related_name='packages')
    name = models.CharField(max_length=50, choices=PACKAGE_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_days = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(90)])
    revisions = models.IntegerField(default=1)
    features = models.TextField(help_text="Line separated features")
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['price']
    
    def __str__(self):
        return f"{self.gig.title} - {self.name}"
    
    @property
    def features_list(self):
        return [f.strip() for f in self.features.split('\n') if f.strip()]

class GigRequirement(models.Model):
    TYPE_CHOICES = [
        ('text', 'Text Answer'),
        ('textarea', 'Long Text'),
        ('file', 'File Upload'),
        ('checkbox', 'Checkbox'),
        ('dropdown', 'Dropdown'),
    ]
    
    gig = models.ForeignKey(Gig, on_delete=models.CASCADE, related_name='requirement_items')
    question = models.CharField(max_length=500)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='text')
    required = models.BooleanField(default=True)
    options = models.JSONField(default=list, blank=True, help_text="For dropdown options")
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return self.question

class GigFaq(models.Model):
    """Frequently Asked Questions for gig"""
    gig = models.ForeignKey(Gig, on_delete=models.CASCADE, related_name='faqs')
    question = models.CharField(max_length=500)
    answer = models.TextField()
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return self.question

class SavedGig(models.Model):
    """Client saves gig for later"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_gigs')
    gig = models.ForeignKey(Gig, on_delete=models.CASCADE, related_name='saved_by')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'gig')
    
    def __str__(self):
        return f"{self.user.email} saved {self.gig.title}"