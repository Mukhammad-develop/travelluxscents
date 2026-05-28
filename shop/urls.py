from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.catalog, name='catalog'),
    path('product/<slug:slug>/modal/', views.product_detail_modal, name='product_modal'),
    path('variant/<int:variant_id>/price/', views.get_variant_price, name='variant_price'),
    path('product/<int:product_id>/notify/', views.stock_notify, name='stock_notify'),
    path('discovery-sets/', views.discovery_sets_view, name='discovery_sets'),
    path('discovery-set/<slug:slug>/', views.discovery_set_detail, name='discovery_set_detail'),
    path('mood/<slug:slug>/', views.mood_collection_view, name='mood_collection'),
]
