from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn as uv

from app.api.v1.endpoints import t_shirt_endpoint

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

## add endpoints
app.include_router(t_shirt_endpoint.router)



if __name__ == "__main__":
    uv.run(app, host="0.0.0.0", port=8000)
