from django.urls import path
from . import views
from . import api_views

app_name = 'gigs'

urlpatterns = [

    # ─────────────────────────────────────
    # FRONTEND VIEWS
    # IMPORTANT: Static paths pehle, dynamic slug paths bilkul last mein
    # ─────────────────────────────────────
    path('', views.gig_list, name='gig_list'),
    path('my-gigs/', views.my_gigs, name='my_gigs'),

    # Public — static paths PEHLE
    path('', views.gig_list, name='gig_list'),
    path('category/<slug:slug>/', views.category_gigs, name='category_gigs'),

    # Freelancer — static paths (login required)
    path('create/', views.create_gig, name='create_gig'),        # FIX: pehle tha, ab upar hai
    path('my-gigs/', views.my_gigs, name='my_gigs'),             # FIX: slug se conflict tha
    path('saved/', views.saved_gigs, name='saved_gigs'),         # FIX: slug se conflict tha

    # UUID-based paths
    path('<uuid:gig_id>/edit/', views.edit_gig, name='edit_gig'),
    path('<uuid:gig_id>/delete/', views.delete_gig, name='delete_gig'),
    path('<uuid:gig_id>/toggle/', views.toggle_gig_status, name='toggle_gig'),
    path('<uuid:gig_id>/analytics/', views.gig_analytics, name='gig_analytics'),
    path('save/<uuid:gig_id>/', views.save_gig, name='save_gig'),

    # Dynamic slug — BILKUL LAST MEIN (warna upar ke paths catch ho jaate)
    path('<slug:slug>/', views.gig_detail, name='gig_detail'),

    # ─────────────────────────────────────
    # API ENDPOINTS (Swagger inhe dikhata hai)
    # ─────────────────────────────────────

    # Categories
    path('api/categories/', api_views.CategoryListAPIView.as_view(), name='api_categories'),
    path('api/categories/<int:category_id>/subcategories/', api_views.SubCategoryListAPIView.as_view(), name='api_subcategories'),

    # Gigs — Public
    path('api/gigs/', api_views.GigListAPIView.as_view(), name='api_gig_list'),
    path('api/gigs/<slug:slug>/', api_views.GigDetailAPIView.as_view(), name='api_gig_detail'),

    # Gigs — Freelancer (Authentication required)
    path('api/gigs/create/', api_views.GigCreateAPIView.as_view(), name='api_gig_create'),
    path('api/gigs/my-gigs/', api_views.MyGigsAPIView.as_view(), name='api_my_gigs'),
    path('api/gigs/<uuid:id>/update/', api_views.GigUpdateAPIView.as_view(), name='api_gig_update'),
    path('api/gigs/<uuid:gig_id>/delete/', api_views.GigDeleteAPIView.as_view(), name='api_gig_delete'),
    path('api/gigs/<uuid:gig_id>/toggle/', api_views.GigToggleStatusAPIView.as_view(), name='api_gig_toggle'),
    path('api/gigs/<uuid:gig_id>/analytics/', api_views.GigAnalyticsAPIView.as_view(), name='api_gig_analytics'),

    # Saved Gigs
    path('api/saved/', api_views.SavedGigsListAPIView.as_view(), name='api_saved_gigs'),
    path('api/save/<uuid:gig_id>/', api_views.SaveGigAPIView.as_view(), name='api_save_gig'),

    path('api/gigs/', api_views.GigListAPIView.as_view(), name='api_gig_list'),
    path('api/gigs/<slug:slug>/', api_views.GigDetailAPIView.as_view(), name='api_gig_detail'),
]