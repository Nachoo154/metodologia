from core.supabase_client import supabase


SOLD_PURCHASE_STATUSES = ("paid", "sent", "delivered")


def get_profile_by_email(email):
    return (
        supabase
        .table("profiles")
        .select("id,email,first_name,last_name,role")
        .eq("email", email)
        .limit(1)
        .execute()
    )


def create_purchase_rows(rows):
    return supabase.table("purchases").insert(rows).execute()


def finish_purchase(client, user_id, product_id, amount):
    return client.rpc("finish_purchase", {
        "input_user_id": int(user_id),
        "input_product_id": int(product_id),
        "input_amount": int(amount),
    }).execute()


def get_recent_purchases(limit=100):
    return (
        supabase
        .table("purchases")
        .select(
            "id,created_at,amount,status,product_id,user_id,"
            "products!purchases_product_id_fkey(name,price),"
            "profiles!purchases_user_id_fkey(email,first_name,last_name)"
        )
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )


def get_top_selling_products(limit=10):
    res = (
        supabase
        .table("purchases")
        .select(
            "id,amount,status,product_id,"
            "products!purchases_product_id_fkey(name)"
        )
        .in_("status", list(SOLD_PURCHASE_STATUSES))
        .limit(1000)
        .execute()
    )

    purchases = res.data if res.data else []
    ranking = {}

    for purchase in purchases:
        product_id = purchase.get("product_id")
        amount = int(purchase.get("amount") or 0)
        product = purchase.get("products") or {}

        if not product_id or amount <= 0:
            continue

        if product_id not in ranking:
            ranking[product_id] = {
                "product_id": product_id,
                "name": product.get("name") or "Producto eliminado",
                "quantity": 0,
            }

        ranking[product_id]["quantity"] += amount

    return sorted(
        ranking.values(),
        key=lambda item: item["quantity"],
        reverse=True,
    )[:limit]


def update_purchase_status(purchase_id, status):
    return (
        supabase
        .table("purchases")
        .update({"status": status})
        .eq("id", purchase_id)
        .execute()
    )
