from .supabase_client import supabase


def get_profile_by_email(email):
    return (
        supabase
        .table("profiles")
        .select("id,email,first_name,last_name")
        .eq("email", email)
        .limit(1)
        .execute()
    )


def create_purchase_rows(rows):
    return supabase.table("purchases").insert(rows).execute()


def get_recent_purchases(limit=100):
    return (
        supabase
        .table("purchases")
        .select("id,created_at,amount,status,product_id,user_id,products(name,price),profiles(email,first_name,last_name)")
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )
