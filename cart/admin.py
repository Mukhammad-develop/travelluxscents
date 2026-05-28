from django.contrib import admin
from .models import Cart, CartItem, DiscoveryCartItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ('variant', 'quantity', 'line_total')


class DiscoveryCartItemInline(admin.TabularInline):
    model = DiscoveryCartItem
    extra = 0


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'session_key', 'total_items', 'subtotal', 'created_at')
    inlines = [CartItemInline, DiscoveryCartItemInline]
    readonly_fields = ('session_key',)
