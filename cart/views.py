from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from django.template.loader import render_to_string
from shop.models import ProductVariant, DiscoverySet, Product
from .utils import get_or_create_cart
from .models import CartItem, DiscoveryCartItem


@require_POST
def add_to_cart(request):
    """HTMX: Add a product variant to cart."""
    variant_id = request.POST.get('variant_id')
    quantity = int(request.POST.get('quantity', 1))

    variant = get_object_or_404(ProductVariant, id=variant_id)
    cart = get_or_create_cart(request)

    item, created = CartItem.objects.get_or_create(cart=cart, variant=variant)
    if not created:
        item.quantity += quantity
    else:
        item.quantity = quantity
    item.save()

    count = cart.all_item_count
    return HttpResponse(f'{count}')


@require_POST
def add_discovery_to_cart(request):
    """Add discovery set to cart."""
    set_id = request.POST.get('discovery_set_id')
    product_ids = request.POST.getlist('product_ids')
    ds = get_object_or_404(DiscoverySet, id=set_id)

    if len(product_ids) != ds.pick_count:
        return HttpResponse(
            f'<p class="text-red-400">Please select exactly {ds.pick_count} products.</p>',
            status=400
        )

    cart = get_or_create_cart(request)
    discovery_item = DiscoveryCartItem.objects.create(cart=cart, discovery_set=ds)
    products = Product.objects.filter(id__in=product_ids)
    discovery_item.selected_products.set(products)

    html = render_to_string('partials/cart_badge.html', {'cart_item_count': cart.all_item_count})
    response = HttpResponse(html)
    response['HX-Trigger'] = 'cartUpdated'
    return response


def cart_page(request):
    """Full cart page."""
    cart = get_or_create_cart(request)
    from shop.models import SiteSettings
    settings = SiteSettings.load()
    free_threshold = settings.free_delivery_threshold
    remaining = max(0, free_threshold - cart.grand_total)
    context = {
        'cart': cart,
        'cart_items': cart.items.select_related('variant__product', 'variant__bottle_size', 'variant__bottle_color').all(),
        'discovery_items': cart.discovery_items.select_related('discovery_set').prefetch_related('selected_products').all(),
        'free_threshold': free_threshold,
        'remaining_for_free': remaining,
        'qualifies_free_delivery': cart.grand_total >= free_threshold,
    }
    return render(request, 'cart/cart.html', context)


def cart_mini(request):
    """HTMX: Mini cart sidebar/dropdown."""
    cart = get_or_create_cart(request)
    context = {
        'cart': cart,
        'cart_items': cart.items.select_related('variant__product', 'variant__bottle_size', 'variant__bottle_color').all(),
    }
    return render(request, 'partials/cart_mini.html', context)


@require_POST
def update_cart_item(request, item_id):
    """Update quantity of cart item."""
    cart = get_or_create_cart(request)
    item = get_object_or_404(CartItem, id=item_id, cart=cart)
    quantity = int(request.POST.get('quantity', 1))

    if quantity <= 0:
        item.delete()
    else:
        item.quantity = quantity
        item.save()

    return cart_page(request)


@require_POST
def remove_cart_item(request, item_id):
    """Remove item from cart."""
    cart = get_or_create_cart(request)
    item = get_object_or_404(CartItem, id=item_id, cart=cart)
    item.delete()

    if request.headers.get('HX-Request'):
        return cart_page(request)
    from django.shortcuts import redirect
    return redirect('cart:cart')


@require_POST
def remove_discovery_item(request, item_id):
    """Remove discovery set from cart."""
    cart = get_or_create_cart(request)
    item = get_object_or_404(DiscoveryCartItem, id=item_id, cart=cart)
    item.delete()

    if request.headers.get('HX-Request'):
        return cart_page(request)
    from django.shortcuts import redirect
    return redirect('cart:cart')


def cart_count(request):
    """HTMX: Return just the cart badge count."""
    cart = get_or_create_cart(request)
    return render(request, 'partials/cart_badge.html', {'cart_item_count': cart.all_item_count})
