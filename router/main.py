from fastapi import FastAPI, APIRouter
import uvicorn

app = FastAPI()


@app.get("/hello")
def hello(name: str = ""):
    return {"message": f"Hello {name}"}


if __name__ == "__main__":
   uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)