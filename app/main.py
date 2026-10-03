from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

import app.models
from app.core.config import settings
from app.infrastructure.runtime_config import cors_origin_list
from app.infrastructure.rate_limit import limiter
from app.infrastructure.startup_validation import validate_startup_configuration

from app.database import Base, engine
from app.routers.auth import router as auth_router
from app.routers.category import router as category_router
from app.routers.checkout import router as checkout_router
from app.routers.customer import router as customer_router
from app.routers.payment import router as payment_router
from app.routers.product import router as product_router
from app.routers.receipt import router as receipt_router
from app.routers.sale import router as sale_router
from app.routers.sale_item import router as sale_item_router
from app.routers.supplier import router as supplier_router
from app.routers.user import router as user_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    validate_startup_configuration()

    if settings.app_env.lower() in {"development", "test"}:
        Base.metadata.create_all(bind=engine)

    yield


app = FastAPI(
    title="Agasaro API",
    version="2.0.0",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=(
        ["*"]
        if settings.allow_all_cors
        else [
            *cors_origin_list(settings),

               "https://agasaro-frontend-kldp.vercel.app",

        ]
    ),
    allow_credentials=not settings.allow_all_cors,
    allow_methods=[
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
        "OPTIONS",
    ],
    allow_headers=[
        "Authorization",
        "Content-Type",
        "Idempotency-Key",
        "X-Callback-Secret",
    ],
)

app.include_router(auth_router)
app.include_router(checkout_router)
app.include_router(product_router)
app.include_router(user_router)
app.include_router(customer_router)
app.include_router(category_router)
app.include_router(supplier_router)
app.include_router(sale_router)
app.include_router(sale_item_router)
app.include_router(payment_router)
app.include_router(receipt_router)


@app.get("/", tags=["System"])
def read_root():
    return {
        "status": "success",
        "message": "Agasaro Backend API is active",
        "version": app.version,
    }


@app.get("/healthz", tags=["System"])
def health_check():
    return {"status": "ok"}