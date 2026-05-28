from django.db import models
from django.contrib.auth.models import User
from shop.models import Product, ProductVariant, DiscoverySet


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['session_key']),
            models.Index(fields=['user']),
        ]

    def __str__(self):
        return f"Cart {self.pk} - {'User: ' + str(self.user) if self.user else 'Guest'}"

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def subtotal(self):
        return sum(item.line_total for item in self.items.all())

    @property
    def discovery_subtotal(self):
        return sum(item.line_total for item in self.discovery_items.all())

    @property
    def grand_total(self):
        return self.subtotal + self.discovery_subtotal

    @property
    def all_item_count(self):
        return self.total_items + sum(item.quantity for item in self.discovery_items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('cart', 'variant')

    def __str__(self):
        return f"{self.variant} x {self.quantity}"

    @property
    def line_total(self):
        return self.variant.price * self.quantity


class DiscoveryCartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='discovery_items')
    discovery_set = models.ForeignKey(DiscoverySet, on_delete=models.CASCADE)
    selected_products = models.ManyToManyField(Product)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.discovery_set.name} x {self.quantity}"

    @property
    def line_total(self):
        return self.discovery_set.price * self.quantity
