import json
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from cart.utils import get_or_create_cart
from shop.models import SiteSettings
from .models import Order, OrderItem, DiscoveryOrderItem


def checkout(request):
    """Checkout page."""
    cart = get_or_create_cart(request)
    if cart.all_item_count == 0:
        return redirect('cart:cart')

    site = SiteSettings.load()
    free_threshold = site.free_delivery_threshold
    qualifies_free = cart.grand_total >= free_threshold
    delivery_fee = Decimal('0.00') if qualifies_free else Decimal('3.99')
    total = cart.grand_total + delivery_fee

    context = {
        'cart': cart,
        'cart_items': cart.items.select_related('variant__product', 'variant__bottle_size', 'variant__bottle_color').all(),
        'discovery_items': cart.discovery_items.select_related('discovery_set').prefetch_related('selected_products').all(),
        'delivery_fee': delivery_fee,
        'qualifies_free': qualifies_free,
        'order_total': total,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
    }

    if request.user.is_authenticated:
        profile = getattr(request.user, 'profile', None)
        if profile:
            context['prefill'] = {
                'email': request.user.email,
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'phone': profile.phone,
                'address_line1': profile.address_line1,
                'address_line2': profile.address_line2,
                'city': profile.city,
                'county': profile.county,
                'postcode': profile.postcode,
            }

    return render(request, 'orders/checkout.html', context)


@require_POST
def place_order(request):
    """Process order placement."""
    cart = get_or_create_cart(request)
    if cart.all_item_count == 0:
        return redirect('cart:cart')

    site = SiteSettings.load()
    free_threshold = site.free_delivery_threshold
    subtotal = cart.grand_total
    delivery_fee = Decimal('0.00') if subtotal >= free_threshold else Decimal('3.99')
    total = subtotal + delivery_fee

    email = request.POST.get('email', '').strip()

    # Create order
    order = Order.objects.create(
        email=email,
        first_name=request.POST.get('first_name', ''),
        last_name=request.POST.get('last_name', ''),
        phone=request.POST.get('phone', ''),
        address_line1=request.POST.get('address_line1', ''),
        address_line2=request.POST.get('address_line2', ''),
        city=request.POST.get('city', ''),
        county=request.POST.get('county', ''),
        postcode=request.POST.get('postcode', ''),
        subtotal=subtotal,
        delivery_fee=delivery_fee,
        total=total,
        status='paid',  # In production, set after Stripe confirms
    )

    # Link to user if authenticated
    if request.user.is_authenticated:
        order.user = request.user
        order.save()
    else:
        # Auto-link if email matches existing user
        try:
            user = User.objects.get(email=email)
            order.user = user
            order.save()
        except User.DoesNotExist:
            pass

    # Create order items
    for item in cart.items.select_related('variant__product', 'variant__bottle_size', 'variant__bottle_color').all():
        OrderItem.objects.create(
            order=order,
            product=item.variant.product,
            product_name=item.variant.product.name,
            brand=item.variant.product.brand,
            bottle_size=item.variant.bottle_size.label,
            bottle_color=item.variant.bottle_color.name,
            quantity=item.quantity,
            price=item.variant.price,
        )
        # Decrease stock
        item.variant.stock_quantity = max(0, item.variant.stock_quantity - item.quantity)
        item.variant.save()

    # Discovery items
    for di in cart.discovery_items.select_related('discovery_set').prefetch_related('selected_products').all():
        product_names = ', '.join(p.name for p in di.selected_products.all())
        DiscoveryOrderItem.objects.create(
            order=order,
            discovery_set_name=di.discovery_set.name,
            pick_count=di.discovery_set.pick_count,
            selected_product_names=product_names,
            quantity=di.quantity,
            price=di.discovery_set.price,
        )

    # Clear cart
    cart.items.all().delete()
    cart.discovery_items.all().delete()

    # Send confirmation email
    try:
        email_html = render_to_string('orders/email_confirmation.html', {
            'order': order,
            'items': order.items.all(),
            'discovery_items': order.discovery_items.all(),
            'site_settings': site,
        })
        send_mail(
            subject=f'Order Confirmation #{order.order_id} - {site.site_name}',
            message=f'Thank you for your order #{order.order_id}. Total: £{order.total}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.email],
            html_message=email_html,
            fail_silently=True,
        )
    except Exception:
        pass

    return redirect('orders:confirmation', order_id=order.order_id)


def order_confirmation(request, order_id):
    """Order confirmation page."""
    order = get_object_or_404(Order, order_id=order_id)
    context = {
        'order': order,
        'items': order.items.all(),
        'discovery_items': order.discovery_items.all(),
    }
    return render(request, 'orders/confirmation.html', context)


def order_tracking(request):
    """Track order by ID."""
    order = None
    error = None
    if request.GET.get('order_id'):
        oid = request.GET['order_id'].strip().upper()
        try:
            order = Order.objects.get(order_id=oid)
        except Order.DoesNotExist:
            error = 'Order not found. Please check your order ID.'

    return render(request, 'orders/tracking.html', {'order': order, 'error': error})
