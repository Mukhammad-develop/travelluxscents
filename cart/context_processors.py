from .utils import get_or_create_cart


def cart_context(request):
    cart = get_or_create_cart(request)
    return {
        'cart': cart,
        'cart_item_count': cart.all_item_count if cart else 0,
    }
