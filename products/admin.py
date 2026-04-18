from django.contrib import admin
from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'farmer', 'category', 'price', 'quantity', 'status', 'created_at')
    list_filter = ('status', 'category', 'created_at')
    search_fields = ('name', 'farmer__email', 'location')
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Farmer Info', {'fields': ('farmer',)}),
        ('Product Details', {'fields': ('name', 'description', 'category', 'price', 'quantity', 'unit')}),
        ('Location & Status', {'fields': ('location', 'status')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
