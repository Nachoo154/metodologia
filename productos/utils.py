from productos.services import upload_image


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
        raise ValueError("Precio y stock deben ser números válidos") from exc

    if price < 0:
        raise ValueError("El precio no puede ser negativo")

    if stock < 0:
        raise ValueError("El stock no puede ser negativo")

    if not name or not description:
        raise ValueError("Nombre y descripción son requeridos")

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