from django.contrib import admin
from .models import Order, OrderItem, DiscoveryOrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product_name', 'brand', 'bottle_size', 'bottle_color', 'quantity', 'price', 'line_total')


class DiscoveryOrderItemInline(admin.TabularInline):
    model = DiscoveryOrderItem
    extra = 0
    readonly_fields = ('discovery_set_name', 'pick_count', 'selected_product_names', 'quantity', 'price')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'full_name', 'email', 'total', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    list_editable = ('status',)
    search_fields = ('order_id', 'email', 'first_name', 'last_name')
    readonly_fields = ('order_id', 'created_at', 'updated_at', 'stripe_payment_intent')
    inlines = [OrderItemInline, DiscoveryOrderItemInline]
    fieldsets = (
        ('Order', {'fields': ('order_id', 'status', 'notes')}),
        ('Customer', {'fields': ('user', 'email', 'first_name', 'last_name', 'phone')}),
        ('Shipping', {'fields': ('address_line1', 'address_line2', 'city', 'county', 'postcode', 'country')}),
        ('Payment', {'fields': ('subtotal', 'delivery_fee', 'total', 'stripe_payment_intent')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
