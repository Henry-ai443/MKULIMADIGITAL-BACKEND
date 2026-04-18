from django.db import models
from django.core.validators import MinValueValidator
from users.models import CustomUser
from products.models import Product


class Order(models.Model):
    """Order model - created by buyers/customers"""
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    )

    # Foreign Keys
    buyer = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='orders',
        limit_choices_to={'role__in': ['retailer', 'customer']}
    )

    # Order Details
    order_number = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Delivery Info
    delivery_address = models.TextField()
    phone_number = models.CharField(max_length=20, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['buyer', '-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['order_number']),
        ]

    def __str__(self):
        return f"Order {self.order_number} - {self.buyer.email}"

    def calculate_total(self):
        """Calculate total from order items"""
        total = sum(item.get_subtotal() for item in self.items.all())
        self.total_amount = total
        return total


class OrderItem(models.Model):
    """Individual items in an order"""
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='order_items'
    )

    # Order Details
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        unique_together = ('order', 'product')

    def __str__(self):
        return f"{self.product.name} x {self.quantity} - Order {self.order.order_number}"

    def get_subtotal(self):
        """Calculate subtotal for this item"""
        return self.price_at_purchase * self.quantity
