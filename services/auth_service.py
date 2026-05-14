from .supabase_client import has_service_role, supabase, supabase_auth


def register_user(email, password, first_name="", last_name="", tel=""):
    return supabase_auth.auth.sign_up({
        "email": email,
        "password": password,
        "options": {
            "email_redirect_to": None,
            "data": {
                "first_name": first_name,
                "last_name": last_name,
                "tel": tel or None,
            },
        },
    })


def create_confirmed_user(email, password, first_name="", last_name="", tel=""):
    if has_service_role:
        return supabase.auth.admin.create_user({
            "email": email,
            "password": password,
            "email_confirm": True,
            "user_metadata": {
                "first_name": first_name,
                "last_name": last_name,
                "tel": tel or None,
            },
        })
    return register_user(email, password, first_name, last_name, tel)


def create_profile(profile_data):
    return supabase.table("profiles").insert(profile_data).execute()


def login_user(email, password):
    return supabase_auth.auth.sign_in_with_password({
        "email": email,
        "password": password
    })
