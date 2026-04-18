from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Q
from .models import Order, OrderItem
from .serializers import (
    OrderSerializer,
    OrderDetailSerializer,
    OrderItemSerializer,
    OrderItemCreateSerializer
)
from products.models import Product


class OrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Order model.
    Provides CRUD operations with role-based permissions.
    - List: Buyers see their orders, farmers see orders for their products
    - Create: Only authenticated buyers/retailers
    - Update: Only by admin or order owner
    """
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['order_number', 'buyer__email']
    ordering_fields = ['created_at', 'total_amount', 'status']
    ordering = ['-created_at']

    def get_queryset(self):
        """
        Return orders based on user role:
        - Buyers: See only their own orders
        - Farmers: See orders for their products
        - Admin: See all orders
        """
        user = self.request.user
        
        if user.is_staff or user.role == 'admin':
            # Admins see all orders
            return Order.objects.select_related('buyer').prefetch_related('items')
        
        if user.role == 'farmer':
            # Farmers see orders containing their products
            return Order.objects.filter(
                items__product__farmer=user
            ).distinct().select_related('buyer').prefetch_related('items')
        
        if user.role in ['customer', 'retailer']:
            # Buyers see only their own orders
            return Order.objects.filter(
                buyer=user
            ).select_related('buyer').prefetch_related('items')
        
        return Order.objects.none()

    def get_serializer_class(self):
        """Use detailed serializer for retrieve"""
        if self.action == 'retrieve':
            return OrderDetailSerializer
        return OrderSerializer

    def create(self, request, *args, **kwargs):
        """
        Create a new order with items.
        Expects: {
            "delivery_address": "...",
            "phone_number": "...",
            "items": [
                {"product": 1, "quantity": 5},
                {"product": 2, "quantity": 3}
            ]
        }
        """
        if request.user.role == 'farmer':
            return Response(
                {"error": "Farmers cannot place orders"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        items_data = request.data.pop('items', [])
        
        # Create order
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        
        # Add items to order
        total_amount = 0
        for item_data in items_data:
            try:
                product = Product.objects.get(id=item_data['product'])
                quantity = item_data['quantity']
                
                # Validate stock
                if quantity > product.quantity:
                    order.delete()
                    return Response(
                        {
                            "error": f"Not enough stock for {product.name}. Available: {product.quantity}"
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Create order item
                order_item = OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price_at_purchase=product.price
                )
                total_amount += order_item.get_subtotal()
                
            except Product.DoesNotExist:
                order.delete()
                return Response(
                    {"error": f"Product with id {item_data['product']} not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        # Update order total
        order.total_amount = total_amount
        order.save()
        
        return Response(
            OrderDetailSerializer(order).data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def confirm(self, request, pk=None):
        """Confirm an order (change status from pending to confirmed)"""
        order = self.get_object()
        
        # Only admin or order owner can confirm
        if order.buyer != request.user and not request.user.is_staff:
            return Response(
                {"error": "You can only confirm your own orders"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if order.status != 'pending':
            return Response(
                {"error": f"Cannot confirm order with status: {order.status}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order.status = 'confirmed'
        order.save()
        
        return Response(
            {
                "message": "Order confirmed successfully",
                "order": OrderDetailSerializer(order).data
            },
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def ship(self, request, pk=None):
        """Mark order as shipped (admin/staff only)"""
        order = self.get_object()
        
        if not request.user.is_staff:
            return Response(
                {"error": "Only staff can mark orders as shipped"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if order.status != 'confirmed':
            return Response(
                {"error": f"Cannot ship order with status: {order.status}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order.status = 'shipped'
        order.save()
        
        return Response(
            {
                "message": "Order marked as shipped",
                "order": OrderDetailSerializer(order).data
            },
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def deliver(self, request, pk=None):
        """Mark order as delivered (admin/staff only)"""
        order = self.get_object()
        
        if not request.user.is_staff:
            return Response(
                {"error": "Only staff can mark orders as delivered"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if order.status != 'shipped':
            return Response(
                {"error": f"Cannot deliver order with status: {order.status}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from django.utils import timezone
        order.status = 'delivered'
        order.delivered_at = timezone.now()
        order.save()
        
        return Response(
            {
                "message": "Order marked as delivered",
                "order": OrderDetailSerializer(order).data
            },
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def cancel(self, request, pk=None):
        """Cancel an order"""
        order = self.get_object()
        
        # Only admin or order owner can cancel
        if order.buyer != request.user and not request.user.is_staff:
            return Response(
                {"error": "You can only cancel your own orders"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if order.status in ['shipped', 'delivered']:
            return Response(
                {"error": f"Cannot cancel order with status: {order.status}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order.status = 'cancelled'
        order.save()
        
        return Response(
            {
                "message": "Order cancelled successfully",
                "order": OrderDetailSerializer(order).data
            },
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_orders(self, request):
        """Get orders for the authenticated user"""
        if request.user.role == 'farmer':
            orders = Order.objects.filter(
                items__product__farmer=request.user
            ).distinct()
            serializer = OrderDetailSerializer(orders, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        orders = Order.objects.filter(buyer=request.user)
        serializer = OrderDetailSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get order statistics (admin only)"""
        if not request.user.is_staff:
            return Response(
                {"error": "Only staff can access statistics"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        total_orders = Order.objects.count()
        total_revenue = sum(order.total_amount for order in Order.objects.all())
        
        status_breakdown = {
            'pending': Order.objects.filter(status='pending').count(),
            'confirmed': Order.objects.filter(status='confirmed').count(),
            'shipped': Order.objects.filter(status='shipped').count(),
            'delivered': Order.objects.filter(status='delivered').count(),
            'cancelled': Order.objects.filter(status='cancelled').count(),
        }
        
        return Response(
            {
                "total_orders": total_orders,
                "total_revenue": str(total_revenue),
                "status_breakdown": status_breakdown
            },
            status=status.HTTP_200_OK
        )
