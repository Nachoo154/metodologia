from django.shortcuts import redirect, render
from core.supabase_client import supabase
from pedidos.services import get_profile_by_email, get_recent_purchases, update_purchase_status


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
    purchases_res = get_recent_purchases(100)
    purchases = purchases_res.data if purchases_res.data else []

    return render(request, "vendedor/dashboard.html", {
        "purchases": purchases,
    })


@require_vendedor
def cambiar_estado_pedido(request, id):
    if request.method == "POST":
        status = request.POST.get("status")
        update_purchase_status(id, status)

    return redirect("vendedor_dashboard")

def apply_coupon(request):
    if request.method == "POST":
        coupon_code = request.POST.get("coupon_code", "").strip().upper()

        response = (
            supabase
            .table("coupons")
            .select("*")
            .eq("code", coupon_code)
            .eq("active", True)
            .execute()
        )

        coupons = response.data

        if not coupons:
            print("Cupón inválido")
            return redirect("cart")

        coupon = coupons[0]

        request.session["coupon"] = {
            "id": coupon["id"],
            "code": coupon["code"],
            "discount_percent": float(coupon["discount_percent"]),
        }

        print("Cupón aplicado:", coupon["code"])

    return redirect("cart")