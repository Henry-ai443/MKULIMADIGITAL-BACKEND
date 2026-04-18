from django.db import models
from cloudinary.models import CloudinaryField
from users.models import CustomUser


class Category(models.Model):
    """Product category model"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name


class Product(models.Model):
    """Product model - created by farmers"""
    STATUS_CHOICES = (
        ('available', 'Available'),
        ('out_of_stock', 'Out of Stock'),
        ('discontinued', 'Discontinued'),
    )

    farmer = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='products',
        limit_choices_to={'role': 'farmer'}
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products'
    )

    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField() 
    unit = models.CharField(
        max_length=50,
        default='kg',
        help_text='Unit of measurement (kg, litre, crate, etc.)'
    )

    # Image field for Cloudinary upload
    image = CloudinaryField(
        'product_image',
        folder='mkulima/products/',
        blank=True,
        null=True,
        help_text='Upload product image to Cloudinary'
    )

    location = models.CharField(max_length=255)  # Farm location
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['farmer', '-created_at']),
            models.Index(fields=['category', 'status']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.name} - {self.farmer.email}"

    def is_in_stock(self):
        return self.status == 'available' and self.quantity > 0
