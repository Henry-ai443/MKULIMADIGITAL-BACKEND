from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Q
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for Category model.
    Provides list and retrieve operations.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Product model.
    Provides CRUD operations with role-based permissions.
    - List/Retrieve: Public (anyone)
    - Create/Update/Delete: Only authenticated farmers
    """
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'location', 'farmer__email']
    ordering_fields = ['price', 'created_at', 'quantity']
    ordering = ['-created_at']

    def get_queryset(self):
        """
        Filter products based on query parameters.
        - status: Filter by product status (available, out_of_stock, discontinued)
        - category: Filter by category ID
        - farmer: Filter by farmer ID/email
        - min_price, max_price: Price range filtering
        """
        queryset = Product.objects.select_related('farmer', 'category')
        
        # Filter by status
        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)
        
        # Filter by category
        category_param = self.request.query_params.get('category')
        if category_param:
            queryset = queryset.filter(category_id=category_param)
        
        # Filter by farmer
        farmer_param = self.request.query_params.get('farmer')
        if farmer_param:
            queryset = queryset.filter(
                Q(farmer_id=farmer_param) | Q(farmer__email=farmer_param)
            )
        
        # Price range filtering
        min_price = self.request.query_params.get('min_price')
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        
        max_price = self.request.query_params.get('max_price')
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        
        return queryset

    def perform_create(self, serializer):
        """Automatically set the farmer to the current user"""
        if self.request.user.is_authenticated:
            serializer.save(farmer=self.request.user)
        else:
            return Response(
                {"error": "Authentication required to create products"},
                status=status.HTTP_401_UNAUTHORIZED
            )

    def perform_update(self, serializer):
        """Ensure only the product owner can update"""
        product = self.get_object()
        if product.farmer != self.request.user:
            return Response(
                {"error": "You can only update your own products"},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer.save()

    def perform_destroy(self, instance):
        """Ensure only the product owner can delete"""
        if instance.farmer != self.request.user:
            return Response(
                {"error": "You can only delete your own products"},
                status=status.HTTP_403_FORBIDDEN
            )
        instance.delete()

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_products(self, request):
        """Get all products created by the authenticated farmer"""
        if request.user.role != 'farmer':
            return Response(
                {"error": "Only farmers can access this endpoint"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        products = Product.objects.filter(farmer=request.user)
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def update_stock(self, request, pk=None):
        """Update product stock quantity"""
        product = self.get_object()
        
        if product.farmer != request.user:
            return Response(
                {"error": "You can only update your own products"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        quantity = request.data.get('quantity')
        if quantity is None:
            return Response(
                {"error": "quantity field is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            product.quantity = int(quantity)
            product.save()
            return Response(
                {
                    "message": "Stock updated successfully",
                    "product": ProductSerializer(product).data
                },
                status=status.HTTP_200_OK
            )
        except (ValueError, TypeError):
            return Response(
                {"error": "quantity must be an integer"},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def update_status(self, request, pk=None):
        """Update product status"""
        product = self.get_object()
        
        if product.farmer != request.user:
            return Response(
                {"error": "You can only update your own products"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        new_status = request.data.get('status')
        valid_statuses = ['available', 'out_of_stock', 'discontinued']
        
        if new_status not in valid_statuses:
            return Response(
                {"error": f"Invalid status. Must be one of: {', '.join(valid_statuses)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        product.status = new_status
        product.save()
        return Response(
            {
                "message": "Status updated successfully",
                "product": ProductSerializer(product).data
            },
            status=status.HTTP_200_OK
        )
