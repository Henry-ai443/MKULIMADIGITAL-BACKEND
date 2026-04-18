from rest_framework import serializers
from .models import Order, OrderItem
from products.models import Product
from products.serializers import ProductSerializer
import uuid


class OrderItemSerializer(serializers.ModelSerializer):
    product_details = ProductSerializer(source='product', read_only=True)
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_details', 'quantity', 'price_at_purchase', 'subtotal', 'created_at']
        read_only_fields = ['id', 'created_at', 'price_at_purchase']

    def get_subtotal(self, obj):
        return obj.get_subtotal()


class OrderItemCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating order items"""
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity']

    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError("Quantity must be at least 1.")
        return value


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    buyer_email = serializers.CharField(source='buyer.email', read_only=True)
    buyer_username = serializers.CharField(source='buyer.username', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id',
            'order_number',
            'buyer',
            'buyer_email',
            'buyer_username',
            'status',
            'total_amount',
            'delivery_address',
            'phone_number',
            'items',
            'created_at',
            'updated_at',
            'delivered_at'
        ]
        read_only_fields = ['id', 'order_number', 'buyer', 'total_amount', 'created_at', 'updated_at']

    def create(self, validated_data):
        """Override create to set buyer from request user and generate order number"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['buyer'] = request.user
            # Generate unique order number
            validated_data['order_number'] = f"ORD-{int(uuid.uuid4().int % 100000000):08d}"
        return super().create(validated_data)


class OrderDetailSerializer(serializers.ModelSerializer):
    """Detailed order serializer with all order items"""
    items = OrderItemSerializer(many=True, read_only=True)
    buyer_email = serializers.CharField(source='buyer.email', read_only=True)
    buyer_username = serializers.CharField(source='buyer.username', read_only=True)
    buyer_phone = serializers.CharField(source='buyer.first_name', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id',
            'order_number',
            'buyer',
            'buyer_email',
            'buyer_username',
            'buyer_phone',
            'status',
            'total_amount',
            'delivery_address',
            'phone_number',
            'items',
            'created_at',
            'updated_at',
            'delivered_at'
        ]
