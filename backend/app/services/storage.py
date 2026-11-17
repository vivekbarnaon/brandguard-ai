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

