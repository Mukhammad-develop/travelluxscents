from .models import Cart


def get_or_create_cart(request):
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        # Merge guest cart if exists
        session_key = request.session.session_key
        if session_key:
            guest_carts = Cart.objects.filter(session_key=session_key, user__isnull=True)
            for gc in guest_carts:
                for item in gc.items.all():
                    existing = cart.items.filter(variant=item.variant).first()
                    if existing:
                        existing.quantity += item.quantity
                        existing.save()
                    else:
                        item.cart = cart
                        item.save()
                for di in gc.discovery_items.all():
                    di.cart = cart
                    di.save()
                gc.delete()
        return cart
    else:
        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key
        cart, _ = Cart.objects.get_or_create(session_key=session_key, user__isnull=True)
        return cart
