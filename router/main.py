from fastapi import FastAPI, APIRouter
from supabase import create_client, Client
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/hello")
def hello(name: str = ""):
    return {"message": f"Hello {name}"}


@app.get("/")
def root():
    return {"messege": "have some fun"}


if __name__ == "__main__":
   uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)