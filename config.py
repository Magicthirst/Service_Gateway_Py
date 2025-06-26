import os

from httpx import AsyncClient


protocol = 'http'
host = os.environ.get("HOST") or '0.0.0.0'
port = os.environ.get("PORT") or 8002

run_url = f'{protocol}://{host}:{port}'
auth_url = os.environ.get("AUTH_URL") or 'http://localhost:8000'
hosts_url = os.environ.get("HOSTS_URL") or 'http://localhost:8001'
sync_outlet_url = os.environ.get("SYNC_OUTLET_URL") or 'localhost:8765'
sync_main_url = os.environ.get("SYNC_MAIN_URL") or 'localhost:8766'

async_client = AsyncClient()
