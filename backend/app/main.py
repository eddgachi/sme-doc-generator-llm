from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.security import HTTPBearer

from .routes import read_root
from .services import check_configs_exist, seed_default_configs
from .session import SessionLocal

origins = [
    "http://localhost:5173",
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    with SessionLocal() as db:
        if not check_configs_exist(db):
            seed_default_configs(db)
        pass

    yield  # This will allow the app to start receiving requests
    # Any cleanup logic can be placed after yield, if needed


app = FastAPI(lifespan=lifespan)
security = HTTPBearer()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(read_root)


desc = ""


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_description = f"{desc}\n\n\nmade with ❤️"

    openapi_schema = get_openapi(
        title="SME Doc Generator - Backend APIs",
        version="1.1.0",
        description=openapi_description,
        routes=app.routes,
    )

    # Ensure "components" key exists
    if "components" not in openapi_schema:
        openapi_schema["components"] = {}

    openapi_schema["components"]["securitySchemes"] = {
        "Bearer": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
