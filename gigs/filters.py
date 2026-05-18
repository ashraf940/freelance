import django_filters
from django.db.models import Q
from .models import Gig

class GigFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(method='filter_search')  # search nahi, q rakho
    
    class Meta:
        model = Gig
        fields = ['category', 'sub_category', 'price']
    
    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(title__icontains=value) |
            Q(description__icontains=value)
        )

import django_filters
from django.db.models import Q
from .models import Gig

class GigFilter(django_filters.FilterSet):
    # Search filter using 'q' parameter
    q = django_filters.CharFilter(method='filter_search', label='Search')
    
    # Price range filters
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte', label='Min Price')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte', label='Max Price')
    
    # Delivery time filters
    min_delivery = django_filters.NumberFilter(field_name='delivery_days', lookup_expr='gte', label='Min Days')
    max_delivery = django_filters.NumberFilter(field_name='delivery_days', lookup_expr='lte', label='Max Days')
    
    # Rating filter
    min_rating = django_filters.NumberFilter(field_name='rating', lookup_expr='gte', label='Min Rating')
    
    # Category filter
    category = django_filters.NumberFilter(field_name='category__id', label='Category')
    
    # Sub-category filter
    sub_category = django_filters.NumberFilter(field_name='sub_category__id', label='Sub Category')
    
    class Meta:
        model = Gig
        fields = ['q', 'category', 'sub_category', 'min_price', 'max_price', 'min_delivery', 'max_delivery', 'min_rating']
    
    def filter_search(self, queryset, name, value):
        """Search in title, description, short_description, and tags"""
        if value:
            return queryset.filter(
                Q(title__icontains=value) |
                Q(description__icontains=value) |
                Q(short_description__icontains=value) |
                Q(tags__icontains=value)
            )
        return queryset