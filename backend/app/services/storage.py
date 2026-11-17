import httpx

from app.core.config import get_settings


async def upload_private(path: str, data: bytes, content_type: str) -> None:
    settings = get_settings()
    url = f"{settings.supabase_url.rstrip('/')}/storage/v1/object/{settings.storage_bucket}/{path}"
    headers = {
        "Authorization": f"Bearer {settings.supabase_secret_key.get_secret_value()}",
        "apikey": settings.supabase_secret_key.get_secret_value(),
        "Content-Type": content_type,
        "x-upsert": "false",
    }
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(url, content=data, headers=headers)
    response.raise_for_status()


async def delete_private(path: str) -> None:
    settings = get_settings()
    url = f"{settings.supabase_url.rstrip('/')}/storage/v1/object/remove/{settings.storage_bucket}"
    headers = {"Authorization": f"Bearer {settings.supabase_secret_key.get_secret_value()}", "apikey": settings.supabase_secret_key.get_secret_value()}
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.delete(url, json={"prefixes": [path]}, headers=headers)
    response.raise_for_status()


async def create_signed_url(path: str, expires_in: int = 300) -> str:
    settings = get_settings()
    url = f"{settings.supabase_url.rstrip('/')}/storage/v1/object/sign/{settings.storage_bucket}/{path}"
    headers = {
        "Authorization": f"Bearer {settings.supabase_secret_key.get_secret_value()}",
        "apikey": settings.supabase_secret_key.get_secret_value(),
    }
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(url, json={"expiresIn": expires_in}, headers=headers)
    response.raise_for_status()
    signed_path = response.json().get("signedURL")
    if not isinstance(signed_path, str) or not signed_path:
        raise httpx.HTTPError("Supabase did not return a signed storage URL")
    if signed_path.startswith("/storage/v1/"):
        return f"{settings.supabase_url.rstrip('/')}{signed_path}"
    if signed_path.startswith("/"):
        return f"{settings.supabase_url.rstrip('/')}/storage/v1{signed_path}"
    return signed_path

