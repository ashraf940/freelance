from django.db import models
from django.conf import settings
from django.utils.text import slugify
from ckeditor.fields import RichTextField
import uuid

class BlogCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)
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

class BlogPost(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=500)
    slug = models.SlugField(unique=True, blank=True)
    
    # Research Paper Style Fields
    abstract = models.TextField(help_text="Short summary of the article (100-150 words)")
    keywords = models.CharField(max_length=500, help_text="Comma separated keywords")
    
    # Main Content
    introduction = RichTextField()
    literature_review = RichTextField(blank=True, help_text="Previous studies and existing research")
    methodology = RichTextField(blank=True, help_text="Research methods and data collection")
    analysis = RichTextField(help_text="Main analysis and discussion")
    findings = RichTextField(blank=True, help_text="Key findings and results")
    conclusion = RichTextField()
    references = models.TextField(blank=True, help_text="APA/Harvard style references")
    
    # Meta Information
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='blog_posts')
    category = models.ForeignKey(BlogCategory, on_delete=models.CASCADE, related_name='posts')
    tags = models.CharField(max_length=500, blank=True, help_text="Comma separated tags")
    
    # SEO
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(max_length=500, blank=True)
    
    # Statistics
    views = models.IntegerField(default=0)
    reading_time = models.IntegerField(default=5, help_text="Estimated reading time in minutes")
    
    # Featured Image
    featured_image = models.ImageField(upload_to='blog/', null=True, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-published_at', '-created_at']
        indexes = [
            models.Index(fields=['slug', 'status']),
            models.Index(fields=['-published_at']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while BlogPost.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title
    
    def increment_views(self):
        self.views += 1
        self.save(update_fields=['views'])

class BlogCitation(models.Model):
    """For storing research citations/references"""
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='citations')
    author = models.CharField(max_length=200)
    year = models.IntegerField()
    title = models.CharField(max_length=500)
    source = models.CharField(max_length=500)
    doi = models.CharField(max_length=100, blank=True)
    url = models.URLField(blank=True)
    
    def __str__(self):
        return f"{self.author} ({self.year}) - {self.title}"

class BlogComment(models.Model):
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    comment = models.TextField()
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} on {self.post.title}"