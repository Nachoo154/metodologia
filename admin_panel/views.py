import logging
import os
from usuarios.services import get_all_profiles, update_profile_role

from datetime import datetime

from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt

from productos.services import (
    create_product,
    delete_product,
    get_all_products,
    get_product,
    update_product,
)
from productos.utils import build_product_data
from pedidos.services import get_recent_purchases

logger = logging.getLogger(__name__)

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")
STOCK_MINIMO = 5


def require_admin(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.session.get("admin_authenticated"):
            return redirect("/admin-panel/login/")
        return view_func(request, *args, **kwargs)

    return wrapper


@csrf_exempt
def admin_login(request):
    if request.method == "GET":
        if request.session.get("admin_authenticated"):
            return redirect("/admin-panel/")
        return render(request, "admin_panel/admin_login.html")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            request.session["admin_authenticated"] = True
            return redirect("/admin-panel/")

        return render(request, "admin_panel/admin_login.html", {
            "error": "Usuario o contraseña incorrectos"
        })

    return JsonResponse({"error": "Método no permitido"}, status=405)


def _enrich_purchases(purchases):
    for purchase in purchases:
        product = purchase.get("products") or {}
        price = product.get("price")
        amount = purchase.get("amount") or 0

        if price is not None:
            try:
                purchase["total_amount"] = round(float(price) * int(amount), 2)
            except (TypeError, ValueError):
                purchase["total_amount"] = None
        else:
            purchase["total_amount"] = None

    return purchases


@require_admin
def admin_dashboard(request):
    products = []
    purchases = []
    errors = []

    try:
        res = get_all_products()
        products = res.data if res.data else []
    except Exception as e:
        logger.error(f"Admin dashboard products error: {str(e)}")
        errors.append(f"Productos: {e}")

    try:
        purchases_res = get_recent_purchases(50)
        raw = purchases_res.data if purchases_res.data else []
        purchases = _enrich_purchases(raw)
    except Exception as e:
        logger.exception("Admin dashboard purchases error")
        errors.append(f"Compras: {e}")

    low_stock_count = sum(
        1 for p in products if (p.get("stock") or 0) <= STOCK_MINIMO
    )

    context = {
        "products": products,
        "purchases": purchases,
        "low_stock_count": low_stock_count,
    }

    if errors:
        context["error"] = " | ".join(errors)

    return render(request, "admin_panel/admin_dashboard.html", context)


@require_admin
def admin_product_create(request):
    if request.method == "GET":
        return render(request, "admin_panel/admin_product_form.html", {
            "title": "Crear Producto",
            "button_text": "Crear",
        })

    if request.method == "POST":
        try:
            create_product(build_product_data(request))
            return redirect("/admin-panel/")
        except Exception as e:
            logger.error(f"Product create error: {str(e)}")
            return render(request, "admin_panel/admin_product_form.html", {
                "title": "Crear Producto",
                "button_text": "Crear",
                "error": str(e),
            })

    return JsonResponse({"error": "Método no permitido"}, status=405)


@require_admin
def admin_product_edit(request, id):
    try:
        res = get_product(id)
        product = res.data if res.data else None
    except Exception as e:
        logger.error(f"Product fetch error: {str(e)}")
        return redirect("/admin-panel/")

    if not product:
        return redirect("/admin-panel/")

    if request.method == "GET":
        return render(request, "admin_panel/admin_product_form.html", {
            "title": f"Editar Producto: {product['name']}",
            "button_text": "Guardar Cambios",
            "product": product,
        })

    if request.method == "POST":
        try:
            update_product(id, build_product_data(request))
            return redirect("/admin-panel/")
        except Exception as e:
            logger.error(f"Product edit error: {str(e)}")
            return render(request, "admin_panel/admin_product_form.html", {
                "title": "Editar Producto",
                "button_text": "Guardar Cambios",
                "product": product,
                "error": str(e),
            })

    return JsonResponse({"error": "Método no permitido"}, status=405)


@require_admin
def admin_product_delete(request, id):
    try:
        delete_product(id)
    except Exception as e:
        logger.error(f"Product delete error: {str(e)}")

    return redirect("/admin-panel/")


def admin_logout(request):
    request.session["admin_authenticated"] = False
    return redirect("/admin-panel/login/")


@require_admin
def admin_purchases_data(request):
    try:
        purchases_res = get_recent_purchases(100)
        raw = purchases_res.data if purchases_res.data else []
        purchases = _enrich_purchases(raw)

        return JsonResponse({
            "status": "ok",
            "count": len(purchases),
            "purchases": purchases,
        })

    except Exception as e:
        logger.exception("Admin purchases data error")
        return JsonResponse({
            "status": "error",
            "error": str(e),
        }, status=500)
        
        
@require_admin
def admin_stock(request):
    products = []
    error = None

    try:
        res = get_all_products()
        all_products = res.data if res.data else []
        products = [p for p in all_products if (p.get("stock") or 0) <= STOCK_MINIMO]
        products.sort(key=lambda p: p.get("stock") or 0)
    except Exception as e:
        logger.error(f"Admin stock fetch error: {str(e)}")
        error = str(e)

    return render(request, "admin_panel/admin_stock.html", {
        "products": products,
        "stock_minimo": STOCK_MINIMO,
        "low_stock_count": len(products),
        "error": error,
    })


@require_admin
def admin_stock_report(request):
    try:
        res = get_all_products()
        products = res.data if res.data else []
    except Exception as e:
        logger.error(f"Stock report error: {str(e)}")
        products = []

    products.sort(key=lambda p: p.get("stock") or 0)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [
        "REPORTE DE STOCK DE PRODUCTOS",
        f"Generado: {timestamp}",
        f"Stock minimo configurado: {STOCK_MINIMO}",
        "-" * 60,
        f"{'ID':<6}{'NOMBRE':<35}{'STOCK':>8}  ESTADO",
        "-" * 60,
    ]

    for p in products:
        stock = p.get("stock") or 0
        estado = "BAJO" if stock <= STOCK_MINIMO else "OK"
        nombre = (p.get("name") or "")[:34]
        lines.append(f"{str(p.get('id', '')):<6}{nombre:<35}{stock:>8}  {estado}")

    lines.append("-" * 60)
    lines.append(f"Total de productos: {len(products)}")
    lines.append(
        f"Productos con stock minimo: "
        f"{sum(1 for p in products if (p.get('stock') or 0) <= STOCK_MINIMO)}"
    )

    content = "\n".join(lines) + "\n"
    filename = f"reporte_stock_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

    response = HttpResponse(content, content_type="text/plain; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


@require_admin
def admin_stock_update(request, id):
    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido"}, status=405)

    try:
        new_stock = int(request.POST.get("stock", ""))
        if new_stock < 0:
            raise ValueError("El stock no puede ser negativo")
    except (TypeError, ValueError):
        return redirect("admin_stock")

    try:
        update_product(id, {"stock": new_stock})
    except Exception as e:
        logger.error(f"Stock update error: {str(e)}")

    return redirect("admin_stock")


@require_admin
def admin_users(request):
    profiles_res = get_all_profiles()
    profiles = profiles_res.data if profiles_res.data else []

    low_stock_count = 0
    try:
        res = get_all_products()
        all_products = res.data if res.data else []
        low_stock_count = sum(
            1 for p in all_products if (p.get("stock") or 0) <= STOCK_MINIMO
        )
    except Exception as e:
        logger.error(f"Admin users low_stock_count error: {str(e)}")

    return render(request, "admin_panel/admin_users.html", {
        "profiles": profiles,
        "low_stock_count": low_stock_count,
    })


@require_admin
def admin_update_user_role(request, id):
    if request.method == "POST":
        role = request.POST.get("role")

        if role in ["cliente", "vendedor"]:
            update_profile_role(id, role)

    return redirect("admin_users")