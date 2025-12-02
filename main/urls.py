from django.urls import path
from . import views
from .views import HomeView, ProductListView, ProductDetailView, ManufacturerProductsView
urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.product_list, name='product_list'),
    path('products/<int:product_id>/', views.product_detail, name='product_detail'),
    path('manufacturer/<int:manufacturer_id>/', views.manufacturer_products, name='manufacturer_products'),
    path('products/search/', views.search_products, name='search_products'),
    path('cbv/', HomeView.as_view(), name='home_cbv'),
    path('cbv/products/', ProductListView.as_view(), name='product_list_cbv'),
    path('cbv/products/<int:pk>/', ProductDetailView.as_view(), name='product_detail_cbv'),
    path('cbv/manufacturer/<int:manufacturer_id>/', ManufacturerProductsView.as_view(), name='manufacturer_products_cbv'),
]

