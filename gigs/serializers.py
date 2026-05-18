from rest_framework import serializers
from .models import Gig, Category, SubCategory, GigPackage, GigRequirement, GigFaq, SavedGig


class CategorySerializer(serializers.ModelSerializer):
    gig_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'icon', 'description', 'gig_count', 'is_active']

    def get_gig_count(self, obj):
        return obj.gigs.filter(status='active').count()


class SubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCategory
        fields = ['id', 'name', 'slug', 'is_active']


class GigPackageSerializer(serializers.ModelSerializer):
    features_list = serializers.ListField(read_only=True)

    class Meta:
        model = GigPackage
        fields = ['id', 'name', 'price', 'delivery_days', 'revisions', 'features_list', 'is_active']


class GigRequirementSerializer(serializers.ModelSerializer):
    class Meta:
        model = GigRequirement
        fields = ['id', 'question', 'type', 'required', 'options', 'order']


class GigFaqSerializer(serializers.ModelSerializer):
    class Meta:
        model = GigFaq
        fields = ['id', 'question', 'answer', 'order']


class GigSerializer(serializers.ModelSerializer):
    """
    Gig list ke liye — lightweight
    """
    freelancer_name = serializers.CharField(source='freelancer.get_full_name', read_only=True)
    freelancer_avatar = serializers.ImageField(source='freelancer.avatar', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    average_rating = serializers.DecimalField(max_digits=3, decimal_places=1, read_only=True)

    class Meta:
        model = Gig
        fields = [
            'id', 'title', 'slug', 'short_description', 'price', 'delivery_days',
            'featured_image', 'rating', 'average_rating', 'total_reviews',
            'orders_count', 'status', 'is_featured',
            'freelancer_name', 'freelancer_avatar',
            'category_name', 'created_at',
        ]


class GigDetailSerializer(serializers.ModelSerializer):
    """
    Gig detail ke liye — complete info
    """
    freelancer_name = serializers.CharField(source='freelancer.get_full_name', read_only=True)
    freelancer_avatar = serializers.ImageField(source='freelancer.avatar', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    sub_category_name = serializers.CharField(source='sub_category.name', read_only=True)
    packages = GigPackageSerializer(many=True, read_only=True)
    faqs = GigFaqSerializer(many=True, read_only=True)
    requirement_items = GigRequirementSerializer(many=True, read_only=True)
    average_rating = serializers.DecimalField(max_digits=3, decimal_places=1, read_only=True)

    class Meta:
        model = Gig
        fields = [
            'id', 'title', 'slug', 'description', 'short_description',
            'price', 'delivery_days', 'revisions',
            'featured_image', 'gallery_images', 'video_url',
            'rating', 'average_rating', 'total_reviews', 'orders_count',
            'views', 'status', 'is_featured', 'tags',
            'freelancer_name', 'freelancer_avatar',
            'category_name', 'sub_category_name',
            'packages', 'faqs', 'requirement_items',
            'created_at', 'updated_at',
        ]


class GigCreateSerializer(serializers.ModelSerializer):
    """
    Gig create/update ke liye
    """
    class Meta:
        model = Gig
        fields = [
            'category', 'sub_category', 'title', 'description',
            'short_description', 'price', 'delivery_days', 'revisions',
            'featured_image', 'gallery_images', 'video_url',
            'tags', 'meta_title', 'meta_description',
        ]

    def validate_price(self, value):
        if value < 5:
            raise serializers.ValidationError('Minimum price $5 hai')
        if value > 10000:
            raise serializers.ValidationError('Maximum price $10,000 hai')
        return value

    def validate_title(self, value):
        if len(value) < 10:
            raise serializers.ValidationError('Title kam se kam 10 characters ka hona chahiye')
        return value


class SavedGigSerializer(serializers.ModelSerializer):
    gig = GigSerializer(read_only=True)

    class Meta:
        model = SavedGig
        fields = ['id', 'gig', 'created_at']