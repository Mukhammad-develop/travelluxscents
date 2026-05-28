import json
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.db.models import Q, Min
from django.views.decorators.http import require_POST
from .models import (
    Product, ProductVariant, FragranceNote, OccasionTag,
    MoodCollection, Gender, Longevity, Badge, BottleSize, BottleColor,
    StockNotification, DiscoverySet, SiteSettings,
)


def catalog(request):
    """Homepage = Product catalog."""
    products = Product.objects.prefetch_related(
        'notes', 'badges', 'variants', 'mood_collections', 'occasions'
    ).select_related('longevity', 'gender')

    # Search
    q = request.GET.get('q', '').strip()
    if q:
        products = products.filter(
            Q(name__icontains=q) | Q(brand__icontains=q) |
            Q(notes__name__icontains=q) | Q(occasions__name__icontains=q) |
            Q(description__icontains=q)
        ).distinct()

    # Filters
    note_slug = request.GET.get('note')
    if note_slug:
        products = products.filter(notes__slug=note_slug)

    occasion_slug = request.GET.get('occasion')
    if occasion_slug:
        products = products.filter(occasions__slug=occasion_slug)

    gender_slug = request.GET.get('gender')
    if gender_slug:
        products = products.filter(gender__slug=gender_slug)

    longevity_id = request.GET.get('longevity')
    if longevity_id:
        products = products.filter(longevity_id=longevity_id)

    mood_slug = request.GET.get('mood')
    if mood_slug:
        products = products.filter(mood_collections__slug=mood_slug)

    badge_slug = request.GET.get('badge')
    if badge_slug:
        products = products.filter(badges__slug=badge_slug)

    # Sort
    sort = request.GET.get('sort', 'default')
    if sort == 'price_low':
        products = products.annotate(min_price=Min('variants__price')).order_by('min_price')
    elif sort == 'price_high':
        products = products.annotate(min_price=Min('variants__price')).order_by('-min_price')
    elif sort == 'newest':
        products = products.order_by('-created_at')
    elif sort == 'name':
        products = products.order_by('name')

    products = products.distinct()

    # Recently viewed
    recently_viewed_ids = request.session.get('recently_viewed', [])
    recently_viewed = Product.objects.filter(id__in=recently_viewed_ids).prefetch_related('variants', 'notes')

    # Filter options
    context = {
        'products': products,
        'notes': FragranceNote.objects.all(),
        'occasions': OccasionTag.objects.all(),
        'genders': Gender.objects.all(),
        'longevities': Longevity.objects.all(),
        'moods': MoodCollection.objects.filter(is_active=True),
        'badges': Badge.objects.all(),
        'discovery_sets': DiscoverySet.objects.filter(is_active=True),
        'recently_viewed': recently_viewed,
        'current_filters': {
            'q': q, 'note': note_slug, 'occasion': occasion_slug,
            'gender': gender_slug, 'longevity': longevity_id,
            'mood': mood_slug, 'badge': badge_slug, 'sort': sort,
        },
    }

    if request.headers.get('HX-Request'):
        return render(request, 'partials/product_grid.html', context)

    return render(request, 'shop/catalog.html', context)


def product_detail_modal(request, slug):
    """HTMX modal with bottle selection."""
    product = get_object_or_404(
        Product.objects.prefetch_related('variants__bottle_size', 'variants__bottle_color', 'notes', 'badges', 'images'),
        slug=slug
    )

    # Track recently viewed
    recently_viewed = request.session.get('recently_viewed', [])
    if product.id in recently_viewed:
        recently_viewed.remove(product.id)
    recently_viewed.insert(0, product.id)
    request.session['recently_viewed'] = recently_viewed[:10]

    # Group variants by size
    sizes = BottleSize.objects.filter(
        id__in=product.variants.values_list('bottle_size_id', flat=True)
    ).order_by('order')

    # Build a size→colors→variant map
    size_data = {}
    for size in sizes:
        colors = []
        for variant in product.variants.filter(bottle_size=size).select_related('bottle_color'):
            colors.append({
                'id': variant.id,
                'color_id': variant.bottle_color.id,
                'color_name': variant.bottle_color.name,
                'hex_color': variant.bottle_color.hex_color,
                'price': str(variant.price),
                'in_stock': variant.in_stock,
                'preview_image': variant.preview_image.url if variant.preview_image else '',
            })
        size_data[size.id] = {
            'size_id': size.id,
            'label': size.label,
            'size_ml': size.size_ml,
            'colors': colors,
        }

    context = {
        'product': product,
        'sizes': sizes,
        'size_data_json': json.dumps(size_data),
    }
    return render(request, 'partials/product_modal.html', context)


def get_variant_price(request, variant_id):
    """HTMX endpoint to get variant price."""
    variant = get_object_or_404(ProductVariant, id=variant_id)
    return HttpResponse(f'£{variant.price}')


@require_POST
def stock_notify(request, product_id):
    """Collect email for stock notifications."""
    product = get_object_or_404(Product, id=product_id)
    email = request.POST.get('email', '').strip()
    if email:
        StockNotification.objects.get_or_create(product=product, email=email)
        return HttpResponse('<p class="text-green-400 text-sm mt-2">✓ We\'ll notify you when it\'s back in stock!</p>')
    return HttpResponse('<p class="text-red-400 text-sm mt-2">Please enter a valid email.</p>')


def discovery_sets_view(request):
    """Discovery sets page."""
    sets = DiscoverySet.objects.filter(is_active=True).prefetch_related('included_products')
    return render(request, 'shop/discovery_sets.html', {'discovery_sets': sets})


def discovery_set_detail(request, slug):
    """Modal for selecting products in a discovery set."""
    ds = get_object_or_404(DiscoverySet, slug=slug, is_active=True)
    available = ds.get_available_products().prefetch_related('notes', 'variants')
    context = {
        'discovery_set': ds,
        'available_products': available,
    }
    return render(request, 'partials/discovery_modal.html', context)


def mood_collection_view(request, slug):
    """Mood collection products."""
    mood = get_object_or_404(MoodCollection, slug=slug, is_active=True)
    products = mood.products.filter(in_stock=True).prefetch_related('variants', 'notes', 'badges')
    context = {
        'mood': mood,
        'products': products,
    }
    if request.headers.get('HX-Request'):
        return render(request, 'partials/product_grid.html', {'products': products})
    return render(request, 'shop/mood_collection.html', context)
