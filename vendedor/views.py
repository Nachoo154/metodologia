from datetime import datetime

from django.http import HttpResponse
from django.shortcuts import redirect, render

from pedidos.services import (
    get_profile_by_email,
    get_recent_purchases,
    get_top_selling_products,
    update_purchase_status
)


def require_vendedor(view_func):
    def wrapper(request, *args, **kwargs):
        email = request.session.get("user_email")

        if not email:
            return redirect("login")

        profile_res = get_profile_by_email(email)
        profile = profile_res.data[0] if profile_res.data else None

        if not profile or profile.get("role") != "vendedor":
            return redirect("home")

        return view_func(request, *args, **kwargs)

    return wrapper


@require_vendedor
def vendedor_dashboard(request):
    status_filter = request.GET.get("status", "")

    purchases_res = get_recent_purchases(100)
    purchases = purchases_res.data if purchases_res.data else []

    if status_filter:
        purchases = [
            purchase for purchase in purchases
            if purchase.get("status") == status_filter
        ]

    return render(request, "vendedor/dashboard.html", {
        "purchases": purchases,
        "status_filter": status_filter,
    })


@require_vendedor
def cambiar_estado_pedido(request, id):
    if request.method == "POST":
        status = request.POST.get("status")

        if status:
            update_purchase_status(id, status)

    return redirect("vendedor_dashboard")


@require_vendedor
def reporte_mas_vendidos(request):
    products = get_top_selling_products(10)
    generated_at = datetime.now()

    lines = [
        "REPORTE DE PRODUCTOS MAS VENDIDOS",
        f"Generado: {generated_at.strftime('%Y-%m-%d %H:%M:%S')}",
        "-" * 64,
        f"{'PUESTO':<8}{'PRODUCTO':<44}{'CANTIDAD':>10}",
        "-" * 64,
    ]

    for index, product in enumerate(products, start=1):
        name = (product.get("name") or "Producto eliminado")[:43]
        quantity = product.get("quantity") or 0
        lines.append(f"{index:<8}{name:<44}{quantity:>10}")

    if not products:
        lines.append("No hay ventas registradas para mostrar.")

    lines.append("-" * 64)
    lines.append(f"Total de productos en ranking: {len(products)}")

    content = "\n".join(lines) + "\n"
    filename = f"reporte_mas_vendidos_{generated_at.strftime('%Y%m%d_%H%M%S')}.txt"

    response = HttpResponse(content, content_type="text/plain; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response
