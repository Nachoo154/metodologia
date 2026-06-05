import logging
import os
from usuarios.services import get_all_profiles, update_profile_role

import json
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
from pedidos.services import (
    create_coupon,
    get_all_coupons,
    get_recent_purchases,
    set_coupon_active,
)

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


REQUIRED_IMPORT_FIELDS = ("name", "description", "price", "stock", "image")


def _validate_imported_products(raw):
    if not isinstance(raw, list):
        raise ValueError("El JSON debe ser una lista de productos")

    if not raw:
        raise ValueError("La lista de productos está vacía")

    validated = []
    for index, item in enumerate(raw, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"Producto #{index}: debe ser un objeto JSON")

        missing = [f for f in REQUIRED_IMPORT_FIELDS if f not in item]
        if missing:
            raise ValueError(
                f"Producto #{index}: faltan campos requeridos: {', '.join(missing)}"
            )

        name = str(item["name"]).strip()
        description = str(item["description"]).strip()
        image = str(item["image"]).strip()

        if not name:
            raise ValueError(f"Producto #{index}: el nombre no puede estar vacío")
        if not description:
            raise ValueError(f"Producto #{index}: la descripción no puede estar vacía")
        if not image:
            raise ValueError(f"Producto #{index}: la imagen no puede estar vacía")

        try:
            price = float(item["price"])
        except (TypeError, ValueError):
            raise ValueError(f"Producto #{index}: el precio debe ser numérico")
        try:
            stock = int(item["stock"])
        except (TypeError, ValueError):
            raise ValueError(f"Producto #{index}: el stock debe ser un entero")

        if price < 0:
            raise ValueError(f"Producto #{index}: el precio no puede ser negativo")
        if stock < 0:
            raise ValueError(f"Producto #{index}: el stock no puede ser negativo")

        validated.append({
            "name": name,
            "description": description,
            "price": price,
            "stock": stock,
            "image": image,
        })

    return validated


@require_admin
def admin_product_import(request):
    if request.method == "GET":
        return render(request, "admin_panel/admin_product_import.html", {})

    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido"}, status=405)

    uploaded = request.FILES.get("json_file")
    if not uploaded:
        return render(request, "admin_panel/admin_product_import.html", {
            "error": "Debes seleccionar un archivo .json",
        })

    try:
        raw_text = uploaded.read().decode("utf-8")
    except UnicodeDecodeError:
        return render(request, "admin_panel/admin_product_import.html", {
            "error": "El archivo no tiene codificación UTF-8 válida",
        })

    try:
        parsed = json.loads(raw_text)
    except json.JSONDecodeError as e:
        return render(request, "admin_panel/admin_product_import.html", {
            "error": f"JSON inválido: {e.msg} (línea {e.lineno})",
        })

    try:
        products = _validate_imported_products(parsed)
    except ValueError as e:
        return render(request, "admin_panel/admin_product_import.html", {
            "error": str(e),
        })

    return render(request, "admin_panel/admin_product_import.html", {
        "products": products,
        "products_json": json.dumps(products),
    })


@require_admin
def admin_product_import_confirm(request):
    if request.method != "POST":
        return redirect("admin_product_import")

    payload = request.POST.get("products_json", "")
    try:
        parsed = json.loads(payload)
        products = _validate_imported_products(parsed)
    except (json.JSONDecodeError, ValueError) as e:
        return render(request, "admin_panel/admin_product_import.html", {
            "error": f"No se pudo confirmar la importación: {e}",
        })

    created = 0
    errors = []
    for index, product in enumerate(products, start=1):
        try:
            create_product(product)
            created += 1
        except Exception as e:
            logger.error(f"Bulk import error on product #{index}: {str(e)}")
            errors.append(f"#{index} ({product.get('name')}): {e}")

    return render(request, "admin_panel/admin_product_import.html", {
        "success": f"{created} de {len(products)} productos importados correctamente.",
        "import_errors": errors,
    })


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


@require_admin
def admin_coupons(request):
    coupons = []
    error = None
    success = None

    if request.method == "POST":
        code = request.POST.get("code", "").strip().upper()
        discount_raw = request.POST.get("discount_percent", "").strip()

        try:
            if not code:
                raise ValueError("El código no puede estar vacío")

            discount = float(discount_raw)
            if discount <= 0 or discount > 100:
                raise ValueError("El descuento debe estar entre 0 y 100")

            create_coupon({
                "code": code,
                "discount_percent": discount,
                "active": True,
            })
            success = f"Cupón '{code}' creado correctamente."
        except ValueError as e:
            error = str(e)
        except Exception as e:
            logger.error(f"Coupon create error: {str(e)}")
            error = f"No se pudo crear el cupón: {e}"

    try:
        res = get_all_coupons()
        coupons = res.data if res.data else []
    except Exception as e:
        logger.error(f"Admin coupons fetch error: {str(e)}")
        if not error:
            error = str(e)

    return render(request, "admin_panel/admin_coupons.html", {
        "coupons": coupons,
        "error": error,
        "success": success,
    })


@require_admin
def admin_coupon_toggle(request, id):
    if request.method != "POST":
        return redirect("admin_coupons")

    active = request.POST.get("active") == "true"

    try:
        set_coupon_active(id, active)
    except Exception as e:
        logger.error(f"Coupon toggle error: {str(e)}")

    return redirect("admin_coupons")