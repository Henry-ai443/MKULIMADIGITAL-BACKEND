from rest_framework import serializers
from .models import Category, Product


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'created_at', 'updated_at']


class ProductSerializer(serializers.ModelSerializer):
    farmer_email = serializers.CharField(source='farmer.email', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    is_in_stock = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id',
            'farmer',
            'farmer_email',
            'category',
            'category_name',
            'name',
            'description',
            'price',
            'quantity',
            'unit',
            'image',
            'location',
            'status',
            'is_in_stock',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'farmer', 'created_at', 'updated_at']

    def get_is_in_stock(self, obj):
        return obj.is_in_stock()

    def create(self, validated_data):
        """Override create to set farmer from request user"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['farmer'] = request.user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """Allow farmers to update only their own products"""
        request = self.context.get('request')
        if request and request.user.is_authenticated and instance.farmer != request.user:
            raise serializers.ValidationError("You can only update your own products.")
        return super().update(instance, validated_data)
