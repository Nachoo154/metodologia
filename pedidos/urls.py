from django.urls import path

from . import views

urlpatterns = [
    path("", views.vendedor_dashboard, name="vendedor_dashboard"),
    path("pedido/<int:id>/estado/", views.cambiar_estado_pedido, name="cambiar_estado_pedido"),
]