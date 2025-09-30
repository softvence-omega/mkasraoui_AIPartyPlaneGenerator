from fastapi import FastAPI
from fastapi_utilities.repeat import repeat_every
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
import uvicorn as uv

from app.api.v1.endpoints import generate_card
from app.api.v1.endpoints import t_shirt_endpoint
from app.api.v1.endpoints import generate_party
from app.utils.helper import request_product 
from app.config import PRODUCT_API


@repeat_every(seconds=3600, wait_first=False)  # Refresh every hour
async def refresh_product_data(app : FastAPI):
    print("Refreshing product data...")
    try:
        product = request_product(PRODUCT_API)
        app.state.product_data = product
        return product
    except Exception as e:
        print("Error refreshing product data:", e)
        app.state.product_data = []

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Application startup...")
    try:
        print("First Time Loading Product.....")
        await refresh_product_data(app)
        print("Product loaded successfully.")
    except Exception as e:
        print("Error loading product:", e)
    
    print("Startup complete.")
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(generate_card.router)
app.include_router(t_shirt_endpoint.router)
app.include_router(generate_party.router)


if __name__ == "__main__":
    uv.run("main:app", host="0.0.0.0", port=8000)
