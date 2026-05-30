from django.contrib import admin
from .models import (
    SiteSettings, TrustBadge, Badge, Longevity, OccasionTag,
    MoodCollection, FragranceNote, Gender, BottleSize, BottleColor,
    Product, ProductVariant, ProductImage, StockNotification, DiscoverySet,
)


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ('General', {'fields': ('site_name', 'tagline', 'currency_symbol')}),
        ('Delivery', {'fields': ('free_delivery_threshold', 'free_delivery_text', 'delivery_info')}),
        ('WhatsApp', {'fields': ('whatsapp_number', 'whatsapp_message')}),
        ('Content', {'fields': ('footer_disclaimer', 'account_benefits_text')}),
    )

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(TrustBadge)
class TrustBadgeAdmin(admin.ModelAdmin):
    list_display = ('title', 'icon', 'order', 'is_active')
    list_editable = ('order', 'is_active')


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'color', 'order')
    list_editable = ('order',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Longevity)
class LongevityAdmin(admin.ModelAdmin):
    list_display = ('label', 'hours', 'order')
    list_editable = ('order',)


@admin.register(OccasionTag)
class OccasionTagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'icon', 'order')
    list_editable = ('order',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(MoodCollection)
class MoodCollectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'icon', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(FragranceNote)
class FragranceNoteAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'icon', 'category')
    list_filter = ('category',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Gender)
class GenderAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'order')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(BottleSize)
class BottleSizeAdmin(admin.ModelAdmin):
    list_display = ('label', 'size_ml', 'order')
    list_editable = ('order',)


@admin.register(BottleColor)
class BottleColorAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'hex_color', 'order')
    list_editable = ('order',)
    prepopulated_fields = {'slug': ('name',)}


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    fields = ('bottle_size', 'bottle_color', 'price', 'stock_quantity', 'sku', 'preview_image')


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', 'gender', 'longevity', 'in_stock', 'featured', 'order')
    list_filter = ('in_stock', 'featured', 'gender', 'longevity', 'badges', 'mood_collections')
    list_editable = ('in_stock', 'featured', 'order')
    search_fields = ('name', 'brand', 'description')
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ('notes', 'badges', 'occasions', 'mood_collections')
    inlines = [ProductVariantInline, ProductImageInline]
    fieldsets = (
        (None, {'fields': ('name', 'slug', 'brand', 'description', 'short_description')}),
        ('Media', {'fields': ('image', 'image_hover', 'video_preview')}),
        ('Classification', {'fields': ('gender', 'longevity', 'notes', 'badges', 'occasions', 'mood_collections')}),
        ('Status', {'fields': ('in_stock', 'featured', 'order')}),
    )


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ('product', 'bottle_size', 'bottle_color', 'price', 'stock_quantity', 'sku')
    list_filter = ('bottle_size', 'bottle_color')
    search_fields = ('product__name', 'sku')


@admin.register(StockNotification)
class StockNotificationAdmin(admin.ModelAdmin):
    list_display = ('email', 'product', 'created_at', 'notified')
    list_filter = ('notified',)
    readonly_fields = ('email', 'product', 'created_at')


@admin.register(DiscoverySet)
class DiscoverySetAdmin(admin.ModelAdmin):
    list_display = ('name', 'pick_count', 'bottle_size', 'price', 'original_price', 'is_active', 'order')
    list_editable = ('is_active', 'order')
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ('included_products', 'excluded_products')


# Customize admin site
admin.site.site_header = 'TravelLuxeScent Admin'
admin.site.site_title = 'TravelLuxeScent'
admin.site.index_title = 'Store Management'
