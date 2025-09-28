from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
import uvicorn as uv
import asyncio


from app.api.v1.endpoints import generate_card
from app.api.v1.endpoints import t_shirt_endpoint
from app.api.v1.endpoints import generate_party
from app.utils.helper import request_product 
from app.config import PRODUCT_API


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Application startup...")
    try:
        print("Loading Product.....")
        product = request_product(PRODUCT_API)
        app.state.product_data = product
        print("Product loaded successfully.")
    except Exception as e:
        print("Error loading product:", e)
        app.state.product_data = []
    
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
    uv.run("main:app", host="127.0.0.1", port=8000, reload=True)
