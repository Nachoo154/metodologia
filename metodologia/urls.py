from django.urls import path
from . import views

urlpatterns = [
    # Home
    path('', views.home, name='home'),
    
    # Auth Routes
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    
    # Admin Routes
    path('admin/login/', views.admin_login, name='admin_login'),
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/product/create/', views.admin_product_create, name='admin_product_create'),
    path('admin/product/edit/<int:id>/', views.admin_product_edit, name='admin_product_edit'),
    path('admin/product/delete/<int:id>/', views.admin_product_delete, name='admin_product_delete'),
    path('admin/logout/', views.admin_logout, name='admin_logout'),
    
    # Products Routes (legacy - optional)
    path('products/', views.products_list, name='products_list'),
    path('products/create/', views.product_create, name='product_create'),
    path('products/edit/<int:id>/', views.product_edit, name='product_edit'),
    path('products/delete/<int:id>/', views.product_delete, name='product_delete'),

    # Cart Routes
    path('cart/', views.cart_view, name='cart'),
    path('cart/data/', views.cart_data, name='cart_data'),
    path('cart/add/<int:id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:id>/', views.update_cart_item, name='update_cart_item'),
    path('cart/remove/<int:id>/', views.remove_cart_item, name='remove_cart_item'),
    path('cart/checkout/', views.checkout, name='checkout'),
    path('admin/purchases/data/', views.admin_purchases_data, name='admin_purchases_data'),
]
