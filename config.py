import os

from httpx import AsyncClient


def not_found_env(variable_name):
    raise Exception(f'not found env: {variable_name=}')


protocol = 'http'
host = os.environ.get("IP") or not_found_env()
port = int(os.environ.get("PORT")) or not_found_env()

run_url = f'{protocol}://{host}:{port}'
auth_url = os.environ.get("AUTH_URL") or not_found_env()
hosts_url = os.environ.get("HOSTS_URL") or not_found_env()
sync_outlet_url = os.environ.get("SYNC_OUTLET_URL") or not_found_env()
sync_main_url = os.environ.get("SYNC_MAIN_URL") or not_found_env()

async_client = AsyncClient()
