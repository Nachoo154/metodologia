import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()
load_dotenv("env", override=False)

url = os.getenv("SUPABASE_URL") or os.getenv("NEXT_PUBLIC_SUPABASE_URL")
anon_key = os.getenv("SUPABASE_KEY") or os.getenv("NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY")
service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
has_service_role = bool(service_role_key)

if not url or not anon_key:
    raise ValueError(
        "Las variables de entorno SUPABASE_URL y SUPABASE_KEY deben estar configuradas. "
        "Verifica tu archivo .env"
    )

supabase = create_client(url, service_role_key or anon_key)
supabase_auth = create_client(url, anon_key)
