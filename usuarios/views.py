import logging
import re

from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.http import JsonResponse
from django.shortcuts import redirect, render
from supabase_auth.errors import AuthApiError

from pedidos.services import get_profile_by_email
from usuarios.services import create_confirmed_user, create_profile, login_user

logger = logging.getLogger(__name__)


def is_valid_email(email):
    try:
        validate_email(email)
        return True
    except ValidationError:
        return False


def is_valid_phone(tel):
    return bool(re.match(r"^[0-9 +().-]{7,20}$", tel)) if tel else True


def is_valid_name(name):
    return bool(re.match(r"^[A-Za-zÀ-ÿ ]{2,50}$", name))


def supabase_error_message(exc):
    message = str(exc).lower()

    if "email rate limit exceeded" in message or "rate limit" in message:
        return "Supabase limitó temporalmente el envío de emails. Esperá unos minutos."

    if "already registered" in message or "user already registered" in message:
        return "Ese email ya está registrado."

    if "invalid email" in message or "is invalid" in message:
        return "El email ingresado no es válido."

    if "invalid login credentials" in message:
        return "Email o contraseña incorrectos."

    return str(exc)


def store_session_role(request, email):
    try:
        profile_res = get_profile_by_email(email)
        profile = profile_res.data[0] if profile_res.data else None
        request.session["user_role"] = (profile or {}).get("role") or "cliente"
    except Exception as e:
        logger.error(f"Profile role lookup error: {str(e)}")
        request.session["user_role"] = "cliente"


def require_user(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.session.get("user_email"):
            return redirect("/usuarios/login/")
        return view_func(request, *args, **kwargs)

    return wrapper


def register(request):
    if request.method == "GET":
        return render(request, "usuarios/register.html")

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
            return render(request, "usuarios/register.html", {
                "error": "Todos los campos excepto teléfono son obligatorios",
                "form": form_data,
            })

        if not is_valid_name(first_name) or not is_valid_name(last_name):
            return render(request, "usuarios/register.html", {
                "error": "Nombre y apellido solo pueden contener letras y espacios",
                "form": form_data,
            })

        if not is_valid_email(email):
            return render(request, "usuarios/register.html", {
                "error": "Por favor ingresá un email válido",
                "form": form_data,
            })

        if not is_valid_phone(tel):
            return render(request, "usuarios/register.html", {
                "error": "Teléfono inválido",
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
            return render(request, "usuarios/register.html", {
                "error": supabase_error_message(e),
                "form": form_data,
            })
        except Exception as e:
            logger.error(f"Register error: {str(e)}")
            return render(request, "usuarios/register.html", {
                "error": supabase_error_message(e),
                "form": form_data,
            })

        if not res.user:
            return render(request, "usuarios/register.html", {
                "error": "No se pudo crear el usuario",
                "form": form_data,
            })

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
            return render(request, "usuarios/register.html", {
                "error": "El usuario se creó, pero no se pudo guardar el perfil.",
                "form": form_data,
            })

        login_res = login_user(email, password)

        if login_res.user and login_res.session:
            request.session["user_email"] = login_res.user.email
            request.session["user_token"] = login_res.session.access_token
            store_session_role(request, login_res.user.email)

        return redirect("/")

    return JsonResponse({"error": "Método no permitido"}, status=405)


def login(request):
    if request.method == "GET":
        return render(request, "usuarios/login.html")

    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "").strip()

        if not email or not password:
            return render(request, "usuarios/login.html", {
                "error": "Email y contraseña son requeridos"
            })

        if not is_valid_email(email):
            return render(request, "usuarios/login.html", {
                "error": "Por favor ingresá un email válido"
            })

        try:
            res = login_user(email, password)
        except AuthApiError as e:
            logger.error(f"Login auth error: {str(e)}")
            return render(request, "usuarios/login.html", {
                "error": supabase_error_message(e)
            })
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            return render(request, "usuarios/login.html", {
                "error": str(e)
            })

        if res.user and res.session:
            request.session["user_email"] = res.user.email
            request.session["user_token"] = res.session.access_token
            store_session_role(request, res.user.email)
            return redirect("/")

        return render(request, "usuarios/login.html", {
            "error": "Credenciales inválidas"
        })

    return JsonResponse({"error": "Método no permitido"}, status=405)


def logout(request):
    request.session.flush()
    return redirect("/")