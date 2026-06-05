import json
import logging

from django.http import JsonResponse
from django.shortcuts import redirect, render

from core.supabase_client import get_user_supabase
from pedidos.services import finish_purchase, get_profile_by_email
from productos.services import get_product
from usuarios.views import require_user

logger = logging.getLogger(__name__)


def get_cart_payload(request):
    cart = request.session.get("cart", {})
    items = []
    total = 0

    for product_id, quantity in cart.items():
        try:
            res = get_product(product_id)
            product = res.data if res.data else None
        except Exception as e:
            logger.error(f"Cart product fetch error: {str(e)}")
            product = None

        if not product:
            continue

        price = float(product["price"])
        quantity = int(quantity)
        subtotal = price * quantity
        total += subtotal

        items.append({
            "id": product["id"],
            "name": product["name"],
            "price": price,
            "image": product.get("image"),
            "stock": product.get("stock", 0),
            "quantity": quantity,
            "subtotal": subtotal,
        })

    return {
        "items": items,
        "total": total,
        "cart_count": sum(item["quantity"] for item in items),
    }


@require_user
def cart_view(request):
    payload = get_cart_payload(request)

    items = []
    for item in payload["items"]:
        items.append({
            "product": {
                "id": item["id"],
                "name": item["name"],
                "price": item["price"],
                "image": item["image"],
                "stock": item["stock"],
            },
            "quantity": item["quantity"],
            "subtotal": round(item["subtotal"], 2),
        })

    subtotal = round(payload["total"], 2)
    coupon = request.session.get("coupon")
    discount_amount = 0

    if coupon:
        discount_amount = subtotal * (coupon["discount_percent"] / 100)

    discount_amount = round(discount_amount, 2)
    final_total = round(subtotal - discount_amount, 2)

    checkout_success = request.session.pop("checkout_success", False)

    return render(request, "carrito/carrito.html", {
        "items": items,
        "total": final_total,
        "subtotal": subtotal,
        "coupon": coupon,
        "discount_amount": discount_amount,
        "user_email": request.session.get("user_email"),
        "checkout_success": checkout_success,
    })


@require_user
def add_to_cart(request, id):
    if request.method != "POST":
        return redirect("/productos/")

    cart = request.session.get("cart", {})
    product_id = str(id)

    if request.headers.get("content-type") == "application/json":
        try:
            body = json.loads(request.body.decode("utf-8") or "{}")
        except json.JSONDecodeError:
            body = {}
        quantity = int(body.get("quantity", 1))
    else:
        quantity = int(request.POST.get("quantity", 1))

    cart[product_id] = cart.get(product_id, 0) + max(quantity, 1)
    request.session["cart"] = cart
    request.session.modified = True

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        payload = get_cart_payload(request)
        return JsonResponse({
            "status": "ok",
            "cart_count": payload["cart_count"],
            "cart_items": payload["items"],
            "total": payload["total"],
        })

    return redirect("/carrito/")


@require_user
def cart_data(request):
    payload = get_cart_payload(request)

    return JsonResponse({
        "status": "ok",
        "items": payload["items"],
        "total": payload["total"],
        "cart_count": payload["cart_count"],
    })


@require_user
def update_cart_item(request, id):
    if request.method != "POST":
        return redirect("/carrito/")

    cart = request.session.get("cart", {})
    product_id = str(id)
    quantity = int(request.POST.get("quantity", 1))

    if quantity <= 0:
        cart.pop(product_id, None)
    else:
        cart[product_id] = quantity

    request.session["cart"] = cart
    request.session.modified = True

    return redirect("/carrito/")


@require_user
def remove_cart_item(request, id):
    if request.method == "POST":
        cart = request.session.get("cart", {})
        cart.pop(str(id), None)
        request.session["cart"] = cart
        request.session.modified = True

    return redirect("/carrito/")


@require_user
def checkout_confirm(request):
    payload = get_cart_payload(request)

    if not payload["items"]:
        return redirect("/carrito/")

    checkout_error = request.session.pop("checkout_error", None)

    user_email = request.session.get("user_email")
    profile = None

    if user_email:
        try:
            profile_res = get_profile_by_email(user_email)
            profile = profile_res.data[0] if profile_res.data else None
        except Exception as e:
            logger.error(f"Checkout confirm profile error: {str(e)}")

    items = []
    for item in payload["items"]:
        items.append({
            "product": {
                "id": item["id"],
                "name": item["name"],
                "price": item["price"],
                "image": item["image"],
                "stock": item["stock"],
            },
            "quantity": item["quantity"],
            "subtotal": round(item["subtotal"], 2),
        })

    subtotal = round(payload["total"], 2)
    coupon = request.session.get("coupon")
    discount_amount = 0

    if coupon:
        discount_amount = subtotal * (coupon["discount_percent"] / 100)

    discount_amount = round(discount_amount, 2)
    final_total = round(subtotal - discount_amount, 2)

    return render(request, "carrito/cart_confirm.html", {
        "items": items,
        "subtotal": subtotal,
        "coupon": coupon,
        "discount_amount": discount_amount,
        "total": final_total,
        "cart_count": payload["cart_count"],
        "user_email": user_email,
        "profile": profile,
        "checkout_error": checkout_error,
    })


@require_user
def checkout(request):
    if request.method != "POST":
        return redirect("/carrito/")

    cart = request.session.get("cart", {})

    if not cart:
        return redirect("/carrito/")

    user_token = request.session.get("user_token")
    user_email = request.session.get("user_email")

    if not user_token or not user_email:
        return redirect("/usuarios/login/")

    try:
        profile_res = get_profile_by_email(user_email)
        profile = profile_res.data[0] if profile_res.data else None
    except Exception:
        logger.exception("Checkout profile lookup error")
        request.session["checkout_error"] = "No se pudo verificar tu perfil. Intentá de nuevo."
        request.session.modified = True
        return redirect("/carrito/confirmar/")

    if not profile:
        request.session["checkout_error"] = "No encontramos tu perfil de usuario."
        request.session.modified = True
        return redirect("/carrito/confirmar/")

    coupon = request.session.get("coupon")
    coupon_id = None
    discount_amount = 0

    if coupon:
        coupon_id = coupon["id"]

        payload = get_cart_payload(request)
        subtotal = round(payload["total"], 2)

        discount_amount = subtotal * (coupon["discount_percent"] / 100)
        discount_amount = round(discount_amount, 2)

    client = get_user_supabase(user_token)
    processed = []

    for product_id, quantity in list(cart.items()):
        qty = max(int(quantity), 1)

        try:
            finish_purchase(
                client,
                profile["id"],
                product_id,
                qty,
                coupon_id,
                discount_amount,
            )
            processed.append(product_id)

        except Exception as e:
            logger.exception(f"finish_purchase failed for product {product_id}")

            for pid in processed:
                cart.pop(pid, None)

            request.session["cart"] = cart
            request.session["checkout_error"] = _extract_rpc_message(e)
            request.session.modified = True

            return redirect("/carrito/confirmar/")

    request.session["cart"] = {}
    request.session.pop("coupon", None)
    request.session["checkout_success"] = True
    request.session.modified = True

    return redirect("/carrito/")


def _extract_rpc_message(error):
    msg = getattr(error, "message", None) or str(error)

    for line in str(msg).splitlines():
        line = line.strip()

        if line:
            return line

    return "No se pudo completar la compra. Intentá de nuevo."