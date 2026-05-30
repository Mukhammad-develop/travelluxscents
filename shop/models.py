import uuid
from django.db import models
from django.utils.text import slugify


class SiteSettings(models.Model):
    site_name = models.CharField(max_length=100, default='TravelLuxeScent')
    tagline = models.CharField(max_length=200, default='Premium Fragrance Decants')
    free_delivery_threshold = models.DecimalField(max_digits=6, decimal_places=2, default=40.00)
    free_delivery_text = models.CharField(max_length=200, default='Free Delivery Over £40')
    whatsapp_number = models.CharField(max_length=20, default='+447000000000')
    whatsapp_message = models.CharField(max_length=300, default='Hi! I need help with my order.')
    footer_disclaimer = models.TextField(
        default='This product is independently decanted and re-bottled. We are not affiliated with the original brand.'
    )
    account_benefits_text = models.TextField(
        default='Track your orders, get personalised recommendations, and enjoy faster checkout.'
    )
    currency_symbol = models.CharField(max_length=5, default='£')
    delivery_info = models.TextField(default='Royal Mail 1st Class • 1-2 Business Days')

    class Meta:
        verbose_name = 'Site Settings'
        verbose_name_plural = 'Site Settings'

    def __str__(self):
        return self.site_name

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class TrustBadge(models.Model):
    title = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, help_text='Emoji or icon class', default='✓')
    description = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title


class Badge(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)
    color = models.CharField(max_length=7, default='#D4AF37', help_text='Hex color code')
    text_color = models.CharField(max_length=7, default='#FFFFFF')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Longevity(models.Model):
    label = models.CharField(max_length=30)
    hours = models.PositiveIntegerField(help_text='Minimum hours', default=4)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name_plural = 'Longevities'

    def __str__(self):
        return self.label


class OccasionTag(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=10, blank=True, default='')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class MoodCollection(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=10, blank=True, default='')
    color = models.CharField(max_length=7, default='#D4AF37', help_text='Theme color hex')
    image = models.ImageField(upload_to='moods/', blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class FragranceNote(models.Model):
    CATEGORY_CHOICES = [
        ('top', 'Top Note'),
        ('middle', 'Middle Note'),
        ('base', 'Base Note'),
    ]
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=10, blank=True, default='🌸', help_text='Emoji icon')
    image = models.ImageField(upload_to='notes/', blank=True, null=True)
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES, default='top')

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Gender(models.Model):
    name = models.CharField(max_length=30)
    slug = models.SlugField(unique=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class BottleSize(models.Model):
    size_ml = models.PositiveIntegerField()
    label = models.CharField(max_length=20)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.label


class BottleColor(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)
    hex_color = models.CharField(max_length=7, default='#000000')
    preview_image = models.ImageField(upload_to='bottles/', blank=True, null=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    brand = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    short_description = models.CharField(max_length=300, blank=True)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    image_hover = models.ImageField(upload_to='products/hover/', blank=True, null=True, help_text='GIF or second image for hover')
    video_preview = models.FileField(upload_to='products/videos/', blank=True, null=True)

    # Relations
    notes = models.ManyToManyField(FragranceNote, blank=True, related_name='products')
    badges = models.ManyToManyField(Badge, blank=True, related_name='products')
    longevity = models.ForeignKey(Longevity, on_delete=models.SET_NULL, null=True, blank=True)
    occasions = models.ManyToManyField(OccasionTag, blank=True, related_name='products')
    mood_collections = models.ManyToManyField(MoodCollection, blank=True, related_name='products')
    gender = models.ForeignKey(Gender, on_delete=models.SET_NULL, null=True, blank=True)

    # Stock
    in_stock = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)

    # Meta
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', '-created_at']

    def __str__(self):
        return f"{self.brand} - {self.name}" if self.brand else self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_base_price(self):
        """Return the lowest variant price."""
        variant = self.variants.order_by('price').first()
        return variant.price if variant else 0

    def get_price_range(self):
        prices = self.variants.values_list('price', flat=True)
        if not prices:
            return None, None
        return min(prices), max(prices)

    def get_display_notes(self):
        return self.notes.all()[:4]


class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    bottle_size = models.ForeignKey(BottleSize, on_delete=models.CASCADE)
    bottle_color = models.ForeignKey(BottleColor, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    stock_quantity = models.PositiveIntegerField(default=10)
    sku = models.CharField(max_length=50, unique=True, blank=True)
    preview_image = models.ImageField(upload_to='variants/', blank=True, null=True)

    class Meta:
        unique_together = ('product', 'bottle_size', 'bottle_color')
        ordering = ['bottle_size__order', 'bottle_color__order']

    def __str__(self):
        return f"{self.product.name} - {self.bottle_size.label} - {self.bottle_color.name}"

    def save(self, *args, **kwargs):
        if not self.sku:
            self.sku = f"{self.product.slug[:10]}-{self.bottle_size.size_ml}ml-{self.bottle_color.slug}"[:50]
        super().save(*args, **kwargs)

    @property
    def in_stock(self):
        return self.stock_quantity > 0


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/gallery/')
    alt_text = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Image for {self.product.name}"


class StockNotification(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stock_notifications')
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)
    notified = models.BooleanField(default=False)

    class Meta:
        unique_together = ('product', 'email')

    def __str__(self):
        return f"{self.email} → {self.product.name}"


class DiscoverySet(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    pick_count = models.PositiveIntegerField(help_text='Number of items to pick (e.g. 3, 5, 10)')
    bottle_size = models.ForeignKey(BottleSize, on_delete=models.CASCADE, help_text='Bottle size for this set')
    price = models.DecimalField(max_digits=8, decimal_places=2)
    original_price = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True, help_text='Shown as strikethrough')
    image = models.ImageField(upload_to='discovery/', blank=True, null=True)
    included_products = models.ManyToManyField(Product, blank=True, related_name='discovery_sets', help_text='Leave blank for all products')
    excluded_products = models.ManyToManyField(Product, blank=True, related_name='excluded_discovery_sets')
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_available_products(self):
        if self.included_products.exists():
            return self.included_products.filter(in_stock=True).exclude(pk__in=self.excluded_products.all())
        return Product.objects.filter(in_stock=True).exclude(pk__in=self.excluded_products.all())

    @property
    def savings(self):
        if self.original_price:
            return self.original_price - self.price
        return 0
