import mimetypes
import os
import re
from pathlib import Path
from uuid import uuid4

from .supabase_client import supabase


PRODUCT_IMAGE_BUCKET = os.getenv("SUPABASE_STORAGE_BUCKET", "products")
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}


def _safe_filename(filename):
    stem = Path(filename or "image").stem
    suffix = Path(filename or "").suffix.lower()
    stem = re.sub(r"[^a-zA-Z0-9_-]+", "-", stem).strip("-") or "image"
    return f"{stem}-{uuid4().hex}{suffix}"


def upload_image(uploaded_file):
    if not uploaded_file:
        return ""

    content_type = uploaded_file.content_type or mimetypes.guess_type(uploaded_file.name)[0]
    if content_type not in ALLOWED_IMAGE_TYPES:
        raise ValueError("La imagen debe ser JPG, PNG, WEBP o GIF")

    file_path = f"products/{_safe_filename(uploaded_file.name)}"
    file_bytes = b"".join(uploaded_file.chunks())

    supabase.storage.from_(PRODUCT_IMAGE_BUCKET).upload(
        file_path,
        file_bytes,
        {
            "content-type": content_type,
            "cache-control": "3600",
            "upsert": "false",
        },
    )

    return supabase.storage.from_(PRODUCT_IMAGE_BUCKET).get_public_url(file_path)

def get_all_products():
    return supabase.table("products").select("*").execute()

def get_product(product_id):
    return supabase.table("products").select("*").eq("id", product_id).single().execute()

def create_product(data):
    return supabase.table("products").insert(data).execute()

def update_product(product_id, data):
    return supabase.table("products").update(data).eq("id", product_id).execute()

def delete_product(product_id):
    return supabase.table("products").delete().eq("id", product_id).execute()
