from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("django-admin/", admin.site.urls),

    path("", include("core.urls")),
    path("usuarios/", include("usuarios.urls")),
    path("carrito/", include("carrito.urls")),
    path("pedidos/", include("pedidos.urls")),
    path("admin-panel/", include("admin_panel.urls")),
    path("vendedor/", include("vendedor.urls")),
]