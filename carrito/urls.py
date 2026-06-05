from django.urls import path

from . import views

urlpatterns = [
    path("", views.cart_view, name="cart"),
    path("data/", views.cart_data, name="cart_data"),
    path("agregar/<int:id>/", views.add_to_cart, name="add_to_cart"),
    path("actualizar/<int:id>/", views.update_cart_item, name="update_cart_item"),
    path("eliminar/<int:id>/", views.remove_cart_item, name="remove_cart_item"),
    path("confirmar/", views.checkout_confirm, name="checkout_confirm"),
    path("checkout/", views.checkout, name="checkout"),
    path("aplicar-cupon/", views.apply_coupon, name="apply_coupon"),
]