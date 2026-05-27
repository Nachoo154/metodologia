from django.shortcuts import redirect, render

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