from fastapi import FastAPI, HTTPException, Depends
# from supabase import create_client, Client
from pydantic import BaseModel
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from fastapi_jwt import JwtAuthorizationCredentials, JwtAccessBearer
# from supabase import create_client, Client
import datetime
from sqlalchemy.orm import Session
from models import Transaction, SessionLocal, Base, User, Credit, Session, Target

def get_hash(input_string: str) -> str:
    import hashlib
    string_hash = hashlib.sha256(input_string.encode("utf-8")).hexdigest()
    return string_hash


app = FastAPI()

url: str = "https://vrwzhwkdvwuyshvzcjvt.supabase.co"
key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZyd3pod2tkdnd1eXNodnpjanZ0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzI3NTI2NTQsImV4cCI6MjA0ODMyODY1NH0.82MpAR5bWTTlQNzmlW1vNaomMygFiDu7mMCXGDT2s8I"
# supabase: Client = create_client(url, key)
access_security = JwtAccessBearer(secret_key="secret_key", auto_error=True)
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


'''class UserSingInData(BaseModel):
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
'''

######### TRANSACTIONS #########

class TransactionData(BaseModel):
    """
    Модель данных для транзакции.

    Атрибуты:
    - user_id (int): Идентификатор пользователя, связанного с транзакцией.
    - amount (float): Сумма транзакции.
    - category (str): Категория транзакции.
    - date (datetime.date): Дата транзакции.
    - type (str): Тип транзакции (например, доход или расход).
    - target_id (int, optional): Идентификатор цели, связанной с транзакцией.
    - credit_id (int, optional): Идентификатор кредита, связанного с транзакцией.
    """
    user_id: int
    amount: float
    category: str
    date: datetime.date
    type: str
    target_id: int = None
    credit_id: int = None

def get_db():
    """
    Создает и возвращает сессию базы данных.

    Используется для управления подключением к базе данных в течение запроса.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/transactions/", response_model=Transaction)
def add_transaction(transaction_data: TransactionData, db: Session = Depends(get_db)):
    """
    Создает новую транзакцию.

    Параметры:
    - transaction_data (TransactionData): Данные для создания транзакции.
    - db (Session): Сессия базы данных.

    Возвращает:
    - Созданную транзакцию.
    """
    transaction = Transaction(**transaction_data.dict())
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction

@app.put("/transactions/{transaction_id}", response_model=Transaction)
def edit_transaction(transaction_id: int, transaction_data: TransactionData, db: Session = Depends(get_db)):
    """
    Редактирует существующую транзакцию.

    Параметры:
    - transaction_id (int): Идентификатор редактируемой транзакции.
    - transaction_data (TransactionData): Новые данные для транзакции.
    - db (Session): Сессия базы данных.

    Возвращает:
    - Обновленную транзакцию.

    Исключения:
    - HTTPException: Если транзакция не найдена.
    """
    transaction = db.query(Transaction).filter(Transaction.transaction_id == transaction_id).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    for key, value in transaction_data.dict().items():
        setattr(transaction, key, value)
    db.commit()
    db.refresh(transaction)
    return transaction

@app.delete("/transactions/{transaction_id}")
def delete_transaction(transaction_id: int, db: Session = Depends(get_db)):
    """
    Удаляет существующую транзакцию.

    Параметры:
    - transaction_id (int): Идентификатор удаляемой транзакции.
    - db (Session): Сессия базы данных.

    Возвращает:
    - Подтверждение удаления транзакции.

    Исключения:
    - HTTPException: Если транзакция не найдена.
    """
    transaction = db.query(Transaction).filter(Transaction.transaction_id == transaction_id).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    db.delete(transaction)
    db.commit()
    return {"detail": "Transaction deleted"}

######### END TRANSACTIONS #########

######### CREDIT #########

class CreditData(BaseModel):
    user_id: int
    name: str
    comment: str = None
    amount: float
    procent: float
    date_start: datetime.date
    date_end_plan: datetime.date
    date_end_fact: datetime.date = None
    type: str

@app.post("/credits/", response_model=Credit)
def add_credit(credit_data: CreditData, db: Session = Depends(get_db)):
    """
    Создает новый кредит.

    Параметры:
    - credit_data (CreditData): Данные для создания кредита.
    - db (Session): Сессия базы данных.

    Возвращает:
    - Созданный кредит.
    """
    credit = Credit(**credit_data.dict())
    db.add(credit)
    db.commit()
    db.refresh(credit)
    return credit

@app.put("/credits/{credit_id}", response_model=Credit)
def edit_credit(credit_id: int, credit_data: CreditData, db: Session = Depends(get_db)):
    """
    Редактирует существующий кредит.

    Параметры:
    - credit_id (int): Идентификатор редактируемого кредита.
    - credit_data (CreditData): Новые данные для кредита.
    - db (Session): Сессия базы данных.

    Возвращает:
    - Обновленный кредит.

    Исключения:
    - HTTPException: Если кредит не найден.
    """
    credit = db.query(Credit).filter(Credit.credit_id == credit_id).first()
    if not credit:
        raise HTTPException(status_code=404, detail="Credit not found")
    for key, value in credit_data.dict().items():
        setattr(credit, key, value)
    db.commit()
    db.refresh(credit)
    return credit

@app.delete("/credits/{credit_id}")
def delete_credit(credit_id: int, db: Session = Depends(get_db)):
    """
    Удаляет существующий кредит.

    Параметры:
    - credit_id (int): Идентификатор удаляемого кредита.
    - db (Session): Сессия базы данных.

    Возвращает:
    - Подтверждение удаления кредита.

    Исключения:
    - HTTPException: Если кредит не найден.
    """
    credit = db.query(Credit).filter(Credit.credit_id == credit_id).first()
    if not credit:
        raise HTTPException(status_code=404, detail="Credit not found")
    db.delete(credit)
    db.commit()
    return {"detail": "Credit deleted"}

######### END CREDIT #########

######### TARGET #########

class TargetData(BaseModel):
    user_id: int
    name: str
    comment: str = None
    amount: float
    date_start: datetime.date
    date_end: datetime.date

@app.post("/targets/", response_model=Target)
def add_target(target_data: TargetData, db: Session = Depends(get_db)):
    """
    Создает новую цель.

    Параметры:
    - target_data (TargetData): Данные для создания цели.
    - db (Session): Сессия базы данных.

    Возвращает:
    - Созданную цель.
    """
    target = Target(**target_data.dict())
    db.add(target)
    db.commit()
    db.refresh(target)
    return target

@app.put("/targets/{target_id}", response_model=Target)
def edit_target(target_id: int, target_data: TargetData, db: Session = Depends(get_db)):
    """
    Редактирует существующую цель.

    Параметры:
    - target_id (int): Идентификатор редактируемой цели.
    - target_data (TargetData): Новые данные для цели.
    - db (Session): Сессия базы данных.

    Возвращает:
    - Обновленную цель.

    Исключения:
    - HTTPException: Если цель не найдена.
    """
    target = db.query(Target).filter(Target.target_id == target_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="Target not found")
    for key, value in target_data.dict().items():
        setattr(target, key, value)
    db.commit()
    db.refresh(target)
    return target

@app.delete("/targets/{target_id}")
def delete_target(target_id: int, db: Session = Depends(get_db)):
    """
    Удаляет существующую цель.

    Параметры:
    - target_id (int): Идентификатор удаляемой цели.
    - db (Session): Сессия базы данных.

    Возвращает:
    - Подтверждение удаления цели.

    Исключения:
    - HTTPException: Если цель не найдена.
    """
    target = db.query(Target).filter(Target.target_id == target_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="Target not found")
    db.delete(target)
    db.commit()
    return {"detail": "Target deleted"}

######### END TARGET #########

if __name__ == "__main__":
   uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)