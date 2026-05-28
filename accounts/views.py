from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import UserProfile
from orders.models import Order


def register_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        password2 = request.POST.get('password2', '')
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()

        if password != password2:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'accounts/register.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'An account with this email already exists.')
            return render(request, 'accounts/register.html')

        user = User.objects.create_user(
            username=email, email=email, password=password,
            first_name=first_name, last_name=last_name,
        )
        UserProfile.objects.create(user=user)

        # Auto-link guest orders
        Order.objects.filter(email=email, user__isnull=True).update(user=user)

        login(request, user)
        messages.success(request, 'Welcome! Your account has been created.')
        return redirect('accounts:dashboard')

    return render(request, 'accounts/register.html')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=email, password=password)
        if user:
            login(request, user)
            next_url = request.GET.get('next', 'accounts:dashboard')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid email or password.')

    return render(request, 'accounts/login.html')


def logout_view(request):
    logout(request)
    return redirect('shop:catalog')


@login_required
def dashboard(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    context = {
        'orders': orders,
        'profile': profile,
    }
    return render(request, 'accounts/dashboard.html', context)


@login_required
def edit_profile(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        request.user.first_name = request.POST.get('first_name', '')
        request.user.last_name = request.POST.get('last_name', '')
        request.user.save()

        profile.phone = request.POST.get('phone', '')
        profile.address_line1 = request.POST.get('address_line1', '')
        profile.address_line2 = request.POST.get('address_line2', '')
        profile.city = request.POST.get('city', '')
        profile.county = request.POST.get('county', '')
        profile.postcode = request.POST.get('postcode', '')
        profile.save()

        messages.success(request, 'Profile updated successfully.')
        return redirect('accounts:dashboard')

    return render(request, 'accounts/edit_profile.html', {'profile': profile})
