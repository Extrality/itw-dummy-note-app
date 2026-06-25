import os

from litestar import Litestar
from litestar.config.cors import CORSConfig
from litestar.openapi.config import OpenAPIConfig

from .db import init_db
from .routes import note_router


async def on_startup():
    await init_db()


CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://127.0.0.1:8000").split(",")

app = Litestar(
    route_handlers=[note_router],
    on_startup=[on_startup],
    cors_config=CORSConfig(allow_origins=CORS_ORIGINS),
    openapi_config=OpenAPIConfig(title="Note API", version="0.1.0"),
)
