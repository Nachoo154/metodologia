import json
import logging
import os
import re

from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from supabase_auth.errors import AuthApiError

from services.auth_service import create_confirmed_user, create_profile, login_user
from services.product_service import (
    create_product,
    delete_product,
    get_all_products,
    get_product,
    update_product,
    upload_image,
)
from services.purchase_service import (
    create_purchase_rows,
    get_profile_by_email,
    get_recent_purchases,
)


logger = logging.getLogger(__name__)

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")


def is_valid_email(email):
    try:
        validate_email(email)
        return True
    except ValidationError:
        return False


def is_valid_phone(tel):
    return bool(re.match(r"^[0-9 +().-]{7,20}$", tel)) if tel else True


def supabase_error_message(exc):
    message = str(exc).lower()
    if "email rate limit exceeded" in message or "rate limit" in message:
        return (
            "Supabase limito temporalmente el envio de emails de confirmacion. "
            "Espera unos minutos antes de registrar otro usuario o usa emails unicos de prueba."
        )
    if "already registered" in message or "user already registered" in message:
        return "Ese email ya esta registrado. Inicia sesion o usa otro email."
    if "invalid email" in message or "is invalid" in message:
        return "El email ingresado no es valido. Revisa que no tenga espacios y que el dominio exista."
    if "invalid login credentials" in message:
        return "No existe una cuenta con ese email o la contrasena es incorrecta."
    return str(exc)


def build_product_data(request):
    name = request.POST.get("name", "").strip()
    description = request.POST.get("description", "").strip()
    image_url = request.POST.get("image_url", "").strip()
    current_image = request.POST.get("current_image", "").strip()
    uploaded_file = request.FILES.get("image")

    try:
        price = float(request.POST.get("price", ""))
        stock = int(request.POST.get("stock", ""))
    except ValueError as exc:
        raise ValueError("Precio y stock deben ser numeros validos") from exc

    if price < 0:
        raise ValueError("El precio no puede ser negativo")
    if stock < 0:
        raise ValueError("El stock no puede ser negativo")
    if not name or not description:
        raise ValueError("Nombre y descripcion son requeridos")

    image = upload_image(uploaded_file) if uploaded_file else image_url or current_image
    if not image:
        raise ValueError("Debes subir una imagen o ingresar una URL de imagen")

    return {
        "name": name,
        "price": price,
        "description": description,
        "stock": stock,
        "image": image,
    }


def require_admin(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.session.get("admin_authenticated"):
            return redirect("/admin/login/")
        return view_func(request, *args, **kwargs)

    return wrapper


def require_user(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.session.get("user_email"):
            return redirect("/login/")
        return view_func(request, *args, **kwargs)

    return wrapper


def home(request):
    try:
        res = get_all_products()
        products = res.data if res.data else []
    except Exception as e:
        logger.error(f"Home products error: {str(e)}")
        products = []

    return render(request, "index.html", {
        "products": products,
        "user_email": request.session.get("user_email"),
        "cart_count": sum(request.session.get("cart", {}).values()),
    })


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


def register(request):
    if request.method == "GET":
        return render(request, "register.html")

    if request.method == "POST":
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "").strip()
        tel = request.POST.get("tel", "").strip()
        form_data = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "tel": tel,
        }

        if not first_name or not last_name or not email or not password:
            return render(request, "register.html", {
                "error": "Todos los campos excepto telefono son obligatorios",
                "form": form_data,
            })
        if not is_valid_email(email):
            return render(request, "register.html", {
                "error": "Por favor ingresa un email valido",
                "form": form_data,
            })
        if not is_valid_phone(tel):
            return render(request, "register.html", {
                "error": "Telefono invalido",
                "form": form_data,
            })

        try:
            res = create_confirmed_user(
                email,
                password,
                first_name=first_name,
                last_name=last_name,
                tel=tel,
            )
        except AuthApiError as e:
            logger.error(f"Register auth error: {str(e)}")
            return render(request, "register.html", {
                "error": supabase_error_message(e),
                "form": form_data,
            })
        except Exception as e:
            logger.error(f"Register error: {str(e)}")
            return render(request, "register.html", {
                "error": supabase_error_message(e),
                "form": form_data,
            })

        if not res.user:
            return render(request, "register.html", {"error": "No se pudo crear el usuario"})

        profile_data = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "tel": tel,
        }

        try:
            create_profile(profile_data)
        except Exception as e:
            logger.error(f"Profile insert error: {str(e)}")
            return render(request, "register.html", {
                "error": "El usuario se creo, pero no se pudo guardar el perfil. Intenta de nuevo mas tarde.",
                "form": form_data,
            })

        login_res = login_user(email, password)
        if login_res.user and login_res.session:
            request.session["user_email"] = login_res.user.email
            request.session["user_token"] = login_res.session.access_token

        return redirect("/")

    return JsonResponse({"error": "Metodo no permitido"}, status=405)


def login(request):
    if request.method == "GET":
        return render(request, "login.html")

    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "").strip()

        if not email or not password:
            return render(request, "login.html", {"error": "Email y contrasena son requeridos"})
        if not is_valid_email(email):
            return render(request, "login.html", {"error": "Por favor ingresa un email valido"})

        try:
            res = login_user(email, password)
        except AuthApiError as e:
            logger.error(f"Login auth error: {str(e)}")
            return render(request, "login.html", {"error": supabase_error_message(e)})
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            return render(request, "login.html", {"error": str(e)})

        if res.user and res.session:
            request.session["user_email"] = res.user.email
            request.session["user_token"] = res.session.access_token
            return redirect("/")

        return render(request, "login.html", {"error": "Credenciales invalidas"})

    return JsonResponse({"error": "Metodo no permitido"}, status=405)


@csrf_exempt
def admin_login(request):
    if request.method == "GET":
        if request.session.get("admin_authenticated"):
            return redirect("/admin/")
        return render(request, "admin_login.html")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            request.session["admin_authenticated"] = True
            return redirect("/admin/")

        return render(request, "admin_login.html", {"error": "Usuario o contrasena incorrectos"})

    return JsonResponse({"error": "Metodo no permitido"}, status=405)


@require_admin
def admin_dashboard(request):
    try:
        res = get_all_products()
        products = res.data if res.data else []
        purchases_res = get_recent_purchases(50)
        purchases = purchases_res.data if purchases_res.data else []
        return render(request, "admin_dashboard.html", {"products": products, "purchases": purchases})
    except Exception as e:
        logger.error(f"Admin dashboard error: {str(e)}")
        return render(request, "admin_dashboard.html", {"products": [], "purchases": [], "error": str(e)})


@require_admin
def admin_product_create(request):
    if request.method == "GET":
        return render(request, "admin_product_form.html", {
            "title": "Crear Producto",
            "button_text": "Crear",
        })

    if request.method == "POST":
        try:
            create_product(build_product_data(request))
            return redirect("/admin/")
        except Exception as e:
            logger.error(f"Product create error: {str(e)}")
            return render(request, "admin_product_form.html", {
                "title": "Crear Producto",
                "button_text": "Crear",
                "error": str(e),
            })

    return JsonResponse({"error": "Metodo no permitido"}, status=405)


@require_admin
def admin_product_edit(request, id):
    try:
        res = get_product(id)
        product = res.data if res.data else None
    except Exception as e:
        logger.error(f"Product fetch error: {str(e)}")
        return redirect("/admin/")

    if not product:
        return redirect("/admin/")

    if request.method == "GET":
        return render(request, "admin_product_form.html", {
            "title": f"Editar Producto: {product['name']}",
            "button_text": "Guardar Cambios",
            "product": product,
        })

    if request.method == "POST":
        try:
            update_product(id, build_product_data(request))
            return redirect("/admin/")
        except Exception as e:
            logger.error(f"Product edit error: {str(e)}")
            return render(request, "admin_product_form.html", {
                "title": "Editar Producto",
                "button_text": "Guardar Cambios",
                "product": product,
                "error": str(e),
            })

    return JsonResponse({"error": "Metodo no permitido"}, status=405)


@require_admin
def admin_product_delete(request, id):
    try:
        delete_product(id)
    except Exception as e:
        logger.error(f"Product delete error: {str(e)}")
    return redirect("/admin/")


def admin_logout(request):
    request.session["admin_authenticated"] = False
    return redirect("/admin/login/")


def logout(request):
    request.session.flush()
    return redirect("/")


def products_list(request):
    try:
        res = get_all_products()
        products = res.data if res.data else []
        return render(request, "products/list.html", {
            "products": products,
            "cart_count": sum(request.session.get("cart", {}).values()),
        })
    except Exception as e:
        logger.error(f"Products list error: {str(e)}")
        return render(request, "products/list.html", {"products": [], "error": str(e)})


@require_admin
def product_create(request):
    if request.method == "GET":
        return render(request, "products/create.html")

    if request.method == "POST":
        try:
            create_product(build_product_data(request))
            return redirect("/products/")
        except Exception as e:
            logger.error(f"Public product create error: {str(e)}")
            return render(request, "products/create.html", {"error": str(e)})

    return JsonResponse({"error": "Metodo no permitido"}, status=405)


@require_admin
def product_edit(request, id):
    try:
        res = get_product(id)
        product = res.data if res.data else None
    except Exception as e:
        logger.error(f"Public product fetch error: {str(e)}")
        return redirect("/products/")

    if not product:
        return redirect("/products/")

    if request.method == "GET":
        return render(request, "products/edit.html", {"product": product})

    if request.method == "POST":
        try:
            update_product(id, build_product_data(request))
            return redirect("/products/")
        except Exception as e:
            logger.error(f"Public product edit error: {str(e)}")
            return render(request, "products/edit.html", {"product": product, "error": str(e)})

    return JsonResponse({"error": "Metodo no permitido"}, status=405)


@require_admin
def product_delete(request, id):
    try:
        delete_product(id)
    except Exception as e:
        logger.error(f"Public product delete error: {str(e)}")
    return redirect("/products/")


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
            "subtotal": item["subtotal"],
        })

    return render(request, "carrito.html", {
        "items": items,
        "total": payload["total"],
        "user_email": request.session.get("user_email"),
    })


@require_user
def add_to_cart(request, id):
    if request.method != "POST":
        return redirect("/products/")

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

    return redirect("/cart/")


@require_user
def cart_data(request):
    payload = get_cart_payload(request)
    return JsonResponse({
        "status": "ok",
        "items": payload["items"],
        "total": payload["total"],
        "cart_count": payload["cart_count"],
    })


@require_admin
def admin_purchases_data(request):
    try:
        purchases_res = get_recent_purchases(100)
        purchases = purchases_res.data if purchases_res.data else []
        return JsonResponse({"status": "ok", "purchases": purchases})
    except Exception as e:
        logger.error(f"Admin purchases data error: {str(e)}")
        return JsonResponse({"status": "error", "error": str(e)}, status=500)


@require_user
def update_cart_item(request, id):
    if request.method != "POST":
        return redirect("/cart/")

    cart = request.session.get("cart", {})
    product_id = str(id)
    quantity = int(request.POST.get("quantity", 1))

    if quantity <= 0:
        cart.pop(product_id, None)
    else:
        cart[product_id] = quantity

    request.session["cart"] = cart
    request.session.modified = True
    return redirect("/cart/")


@require_user
def remove_cart_item(request, id):
    if request.method == "POST":
        cart = request.session.get("cart", {})
        cart.pop(str(id), None)
        request.session["cart"] = cart
        request.session.modified = True

    return redirect("/cart/")


@require_user
def checkout(request):
    if request.method != "POST":
        return redirect("/cart/")

    cart = request.session.get("cart", {})
    if not cart:
        return redirect("/cart/")

    user_email = request.session.get("user_email")
    if not user_email:
        return redirect("/login/")

    profile_res = get_profile_by_email(user_email)
    profile = profile_res.data[0] if profile_res.data else None
    if not profile:
        return redirect("/cart/")

    rows = []
    for product_id, quantity in cart.items():
        qty = max(int(quantity), 1)
        rows.append({
            "product_id": int(product_id),
            "user_id": int(profile["id"]),
            "amount": qty,
            "status": "created",
        })

    create_purchase_rows(rows)

    request.session["cart"] = {}
    request.session.modified = True
    return redirect("/cart/")

