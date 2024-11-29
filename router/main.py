from fastapi import FastAPI, HTTPException
from supabase import create_client, Client
from pydantic import BaseModel
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from fastapi_jwt import JwtAuthorizationCredentials, JwtAccessBearer
from supabase import create_client, Client
import datetime

def get_hash(input_string: str) -> str:
    import hashlib
    string_hash = hashlib.sha256(input_string.encode("utf-8")).hexdigest()
    return string_hash


app = FastAPI()

url: str = "https://vrwzhwkdvwuyshvzcjvt.supabase.co"
key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZyd3pod2tkdnd1eXNodnpjanZ0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzI3NTI2NTQsImV4cCI6MjA0ODMyODY1NH0.82MpAR5bWTTlQNzmlW1vNaomMygFiDu7mMCXGDT2s8I"
supabase: Client = create_client(url, key)
access_security = JwtAccessBearer(secret_key="secret_key", auto_error=True)
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers = ["*"]
)


class UserSingInData(BaseModel):
    login:str
    mail:str
    name_first:str
    name_last:str
    password:str
    host_name:str


@app.post("/singin")
def singin_new_user(user_data: UserSingInData):
    try:
        new_user_data = (supabase.table("users").insert(
            {
                "login": user_data.login,
                "mail": user_data.mail,
                "name_first": user_data.name_first,
                "name_last": user_data.name_last,
                "password_hash":get_hash(user_data.password),
            }
            ).execute())
        
        new_session_data = (supabase.table("sesssions").insert(
            {
                "user_id": new_user_data.data['user_id'],
                "token": access_security.create_access_token(subject={
                    "login": user_data.login
                }),
                "host_name": user_data.host_name,
                "date_start": datetime.datetime.now().strftime("%Y-%m-%d")
            }
            ).execute())
        assert len(new_user_data.data) > 0
        return {"access_token": new_session_data.data['token']}
    except BaseException as e:
        return HTTPException(status_code=401, detail="The user is already registered!")


@app.get("/hello")
def hello(name: str = ""):
    return {"message": f"Hello {name}"}


@app.get("/")
def root():
    return {"messege": "have some fun"}


if __name__ == "__main__":
   uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)