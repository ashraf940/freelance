from django.urls import path
from . import views
from .views import quick_add_blog

app_name = 'blog'

urlpatterns = [
    path('', views.blog_list, name='list'),
    path('<slug:slug>/', views.blog_detail, name='detail'),
    path('category/<slug:slug>/', views.blog_category, name='category'),
    path('comment/<uuid:post_id>/', views.add_comment, name='add_comment'),
    path('quick-add/', quick_add_blog, name='quick_add_blog'),
]