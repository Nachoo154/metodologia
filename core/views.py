import logging

from django.shortcuts import render

from productos.services import get_all_products

logger = logging.getLogger(__name__)


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