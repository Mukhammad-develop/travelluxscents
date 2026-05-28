from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.cart_page, name='cart'),
    path('add/', views.add_to_cart, name='add'),
    path('add-discovery/', views.add_discovery_to_cart, name='add_discovery'),
    path('mini/', views.cart_mini, name='mini'),
    path('update/<int:item_id>/', views.update_cart_item, name='update'),
    path('remove/<int:item_id>/', views.remove_cart_item, name='remove'),
    path('remove-discovery/<int:item_id>/', views.remove_discovery_item, name='remove_discovery'),
    path('count/', views.cart_count, name='count'),
]
