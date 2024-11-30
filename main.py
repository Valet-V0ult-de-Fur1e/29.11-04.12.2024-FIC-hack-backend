import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# from routes.transactions import router as transactions_router
# from routes.credits import router as credits_router
# from routes.targets import router as targets_router
# from routes.users import router as users_router
from transactions import router as transactions_router
from credits import router as credits_router
from targets import router as targets_router
from users import router as users_router
from currency import router as currency_router

app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(users_router, prefix="/users")
app.include_router(transactions_router, prefix="/transactions")
app.include_router(credits_router, prefix="/credits")
app.include_router(targets_router, prefix="/targets")
app.include_router(currency_router, prefix="/currency", tags=["Currency"])

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=3000, reload=True)