from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware
import uvicorn as uv
from app.api.v1.endpoints import generate_card
from app.api.v1.endpoints import t_shirt_endpoint

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(generate_card.router)
app.include_router(t_shirt_endpoint.router)



if __name__ == "__main__":
    uv.run("main:app", host="127.0.0.1", port=8000, reload = True)
