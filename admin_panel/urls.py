from django.urls import path

from . import views

urlpatterns = [
    path("", views.admin_dashboard, name="admin_dashboard"),
    path("login/", views.admin_login, name="admin_login"),
    path("logout/", views.admin_logout, name="admin_logout"),

    path("productos/crear/", views.admin_product_create, name="admin_product_create"),
    path("productos/importar/", views.admin_product_import, name="admin_product_import"),
    path("productos/importar/confirmar/", views.admin_product_import_confirm, name="admin_product_import_confirm"),
    path("productos/<int:id>/editar/", views.admin_product_edit, name="admin_product_edit"),
    path("productos/<int:id>/eliminar/", views.admin_product_delete, name="admin_product_delete"),

    path("compras/data/", views.admin_purchases_data, name="admin_purchases_data"),
    path("usuarios/", views.admin_users, name="admin_users"),
    path("usuarios/<int:id>/rol/", views.admin_update_user_role, name="admin_update_user_role"),

    path("stock/", views.admin_stock, name="admin_stock"),
    path("stock/reporte/", views.admin_stock_report, name="admin_stock_report"),
    path("stock/<int:id>/actualizar/", views.admin_stock_update, name="admin_stock_update"),
]