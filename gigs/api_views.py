from rest_framework import generics, status, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Gig, Category, SubCategory, SavedGig
from .serializers import (
    GigSerializer, GigDetailSerializer, CategorySerializer,
    SubCategorySerializer, SavedGigSerializer, GigCreateSerializer
)
from .filters import GigFilter


# ─────────────────────────────────────────
# CATEGORY ENDPOINTS
# ─────────────────────────────────────────

class CategoryListAPIView(generics.ListAPIView):
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = []

    @swagger_auto_schema(
        operation_summary="All Categories List",
        operation_description="Sab active gig categories return karta hai.",
        tags=["Categories"],
        responses={200: CategorySerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class SubCategoryListAPIView(generics.ListAPIView):
    serializer_class = SubCategorySerializer
    permission_classes = []

    def get_queryset(self):
        return SubCategory.objects.filter(
            category_id=self.kwargs.get('category_id'), is_active=True
        )

    @swagger_auto_schema(
        operation_summary="SubCategories by Category",
        operation_description="Kisi ek category ki subcategories return karta hai.",
        tags=["Categories"],
        responses={200: SubCategorySerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


# ─────────────────────────────────────────
# GIG ENDPOINTS
# ─────────────────────────────────────────

class GigListAPIView(generics.ListAPIView):
    queryset = Gig.objects.filter(status='active').select_related('freelancer', 'category')
    serializer_class = GigSerializer
    permission_classes = []
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = GigFilter
    search_fields = ['title', 'description', 'tags']
    ordering_fields = ['price', 'rating', 'created_at', 'orders_count']
    ordering = ['-is_featured', '-rating']

    # IMPORTANT: manual_parameters bilkul nahi likhna
    # DjangoFilterBackend + SearchFilter + OrderingFilter sab apne aap
    # Swagger mein parameters add karte hain.
    # Manual likhne se "duplicate Parameters found" AssertionError aata hai.
    @swagger_auto_schema(
        operation_summary="Active Gigs List",
        operation_description=(
            "Sab active gigs return karta hai.\n\n"
            "**Filters:** search, category, sub_category, min_price, max_price, "
            "min_delivery, max_delivery, min_rating\n\n"
            "**Ordering:** price, -price, rating, -rating, created_at, orders_count"
        ),
        tags=["Gigs"],
        responses={200: GigSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class GigDetailAPIView(generics.RetrieveAPIView):
    queryset = Gig.objects.filter(status='active').select_related('freelancer', 'category')
    serializer_class = GigDetailSerializer
    lookup_field = 'slug'
    permission_classes = []

    @swagger_auto_schema(
        operation_summary="Gig Detail",
        operation_description="Ek gig ki complete detail slug se return karta hai.",
        tags=["Gigs"],
        responses={200: GigDetailSerializer, 404: "Gig nahi mila"}
    )
    def get(self, request, *args, **kwargs):
        gig = self.get_object()
        gig.increment_views()
        return super().get(request, *args, **kwargs)


class GigCreateAPIView(generics.CreateAPIView):
    serializer_class = GigCreateSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Gig Create (Freelancer Only)",
        operation_description=(
            "Nayi gig create karta hai.\n\n"
            "- User authenticated hona chahiye\n"
            "- User `is_freelancer=True` hona chahiye\n\n"
            "Gig 'pending' mein create hogi — admin approval ke baad active hogi."
        ),
        tags=["Gigs - Freelancer"],
        responses={201: GigSerializer, 400: "Validation error", 403: "Sirf freelancers"}
    )
    def post(self, request, *args, **kwargs):
        if not request.user.is_freelancer:
            return Response(
                {'error': 'Sirf freelancers gig create kar sakte hain'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().post(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(freelancer=self.request.user, status='pending')


class GigUpdateAPIView(generics.UpdateAPIView):
    serializer_class = GigCreateSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        return Gig.objects.filter(freelancer=self.request.user)

    @swagger_auto_schema(
        operation_summary="Gig Update (Owner Only)",
        tags=["Gigs - Freelancer"],
        responses={200: GigSerializer, 403: "Permission denied", 404: "Gig nahi mila"}
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Gig Partial Update",
        tags=["Gigs - Freelancer"],
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)


class GigDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Gig Delete (Soft Delete)",
        operation_description="Gig soft delete — orders hain toh delete nahi hogi.",
        tags=["Gigs - Freelancer"],
        responses={
            200: openapi.Response("Deleted", schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={'message': openapi.Schema(type=openapi.TYPE_STRING)}
            )),
            400: "Orders hain",
            404: "Gig nahi mila"
        }
    )
    def delete(self, request, gig_id):
        gig = get_object_or_404(Gig, id=gig_id, freelancer=request.user)
        if gig.orders_count > 0:
            return Response(
                {'error': 'Orders hain — delete nahi ho sakti'},
                status=status.HTTP_400_BAD_REQUEST
            )
        gig.status = 'deleted'
        gig.save()
        return Response({'message': 'Gig delete ho gayi'})


class GigToggleStatusAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Gig Pause/Activate Toggle",
        operation_description="Active gig pause hogi, paused gig activate hogi.",
        tags=["Gigs - Freelancer"],
        responses={
            200: openapi.Response("Toggled", schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'status': openapi.Schema(type=openapi.TYPE_STRING),
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                }
            )),
            404: "Gig nahi mila"
        }
    )
    def post(self, request, gig_id):
        gig = get_object_or_404(Gig, id=gig_id, freelancer=request.user)
        if gig.status == 'active':
            gig.status = 'paused'
            msg = 'Gig paused ho gayi'
        elif gig.status == 'paused':
            gig.status = 'active'
            msg = 'Gig active ho gayi'
        else:
            return Response(
                {'error': f'Is status ({gig.status}) mein toggle nahi ho sakta'},
                status=status.HTTP_400_BAD_REQUEST
            )
        gig.save()
        return Response({'status': gig.status, 'message': msg})


class MyGigsAPIView(generics.ListAPIView):
    serializer_class = GigSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Gig.objects.filter(freelancer=self.request.user).order_by('-created_at')

    @swagger_auto_schema(
        operation_summary="My Gigs (Freelancer Dashboard)",
        operation_description="Login kiye hue freelancer ke sab gigs — sab statuses ke saath.",
        tags=["Gigs - Freelancer"],
        responses={200: GigSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class GigAnalyticsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Gig Analytics",
        operation_description="Ek gig ki orders, revenue, rating analytics.",
        tags=["Gigs - Freelancer"],
        responses={
            200: openapi.Response("Analytics", schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'gig_id': openapi.Schema(type=openapi.TYPE_STRING),
                    'title': openapi.Schema(type=openapi.TYPE_STRING),
                    'total_orders': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'completed_orders': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'total_revenue': openapi.Schema(type=openapi.TYPE_NUMBER),
                    'average_rating': openapi.Schema(type=openapi.TYPE_NUMBER),
                    'total_views': openapi.Schema(type=openapi.TYPE_INTEGER),
                }
            )),
            404: "Gig nahi mila"
        }
    )
    def get(self, request, gig_id):
        gig = get_object_or_404(Gig, id=gig_id, freelancer=request.user)
        try:
            from orders.models import Order
            from django.db.models import Sum
            orders = Order.objects.filter(gig=gig)
            total_orders = orders.count()
            completed_orders = orders.filter(status='completed').count()
            total_revenue = orders.filter(status='completed').aggregate(
                total=Sum('amount'))['total'] or 0
        except ImportError:
            total_orders = gig.orders_count
            completed_orders = 0
            total_revenue = 0

        return Response({
            'gig_id': str(gig.id),
            'title': gig.title,
            'total_orders': total_orders,
            'completed_orders': completed_orders,
            'total_revenue': float(total_revenue),
            'average_rating': float(gig.rating),
            'total_views': gig.views,
        })


# ─────────────────────────────────────────
# SAVED GIGS ENDPOINTS
# ─────────────────────────────────────────

class SaveGigAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Gig Save/Unsave Toggle",
        operation_description="Pehli call → save. Dobara call → unsave. (Toggle)",
        tags=["Saved Gigs"],
        responses={
            200: openapi.Response("Result", schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'saved': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                }
            )),
            404: "Gig nahi mila"
        }
    )
    def post(self, request, gig_id):
        gig = get_object_or_404(Gig, id=gig_id, status='active')
        saved, created = SavedGig.objects.get_or_create(user=request.user, gig=gig)
        if created:
            return Response({'saved': True, 'message': 'Gig save ho gayi'})
        saved.delete()
        return Response({'saved': False, 'message': 'Gig unsave ho gayi'})


class SavedGigsListAPIView(generics.ListAPIView):
    serializer_class = SavedGigSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return SavedGig.objects.filter(user=self.request.user).select_related('gig')

    @swagger_auto_schema(
        operation_summary="My Saved Gigs",
        operation_description="Login kiye hue user ke sab favorited gigs.",
        tags=["Saved Gigs"],
        responses={200: SavedGigSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)