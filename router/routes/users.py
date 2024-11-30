from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from utils.dependencies import get_db
from schemas import UserSignInData, UserLoginData, UserUpdateData, ExportRequest
from fastapi_jwt import JwtAuthorizationCredentials, JwtAccessBearer
from fastapi.responses import JSONResponse, FileResponse
from utils.hash import get_hash
from utils.export import *
from models import User, Session
from fastapi_jwt import JwtAccessBearer
from datetime import datetime
import pandas as pd
from io import StringIO, BytesIO

from models import Base, User, Session, DATABASE_URL, Transaction, Target, Credit

router = APIRouter()
access_security = JwtAccessBearer(secret_key="secret_key", auto_error=True)

######### USER #########

@router.post("/sign_in", tags=["Users"])
def signin_new_user(user_data: UserSignInData, db: Session = Depends(get_db)):
    if db.query(User).filter((User.login == user_data.login) | (User.mail == user_data.mail)).first():
        raise HTTPException(status_code=400, detail="User already exists")

    new_user = User(
        login=user_data.login,
        mail=user_data.mail,
        name_first=user_data.name_first,
        name_last=user_data.name_last,
        password_hash=get_hash(user_data.password),
    )
    db.add(new_user)
    db.commit()

    token = access_security.create_access_token(subject={"login": user_data.login})
    new_session = Session(
        user_id=new_user.user_id,
        token=token,
        host_name=user_data.host_name,
        date_start=datetime.now().date(),
    )
    db.add(new_session)
    db.commit()

    return {
        "message": "User successfully registered",
        "access_token": token
    }

@router.post("/login", tags=["Users"])
def login_user(user_data: UserLoginData, db: Session = Depends(get_db)):
    user = db.query(User).filter(
        (User.login == user_data.identifier) | (User.mail == user_data.identifier)
    ).first()

    if not user or user.password_hash != get_hash(user_data.password):
        raise HTTPException(status_code=401, detail="Invalid login or password")

    token = access_security.create_access_token(subject={"login": user.login})
    new_session = Session(
        user_id=user.user_id,
        token=token,
        host_name=user_data.host_name,
        date_start=datetime.now().date(),
    )
    db.add(new_session)
    db.commit()
    return {
        "message": "User successfully logged in",
        "access_token": token
    }

@router.post("/logout", tags=["Users"])
def logout_user(credentials: JwtAuthorizationCredentials = Depends(access_security), db: Session = Depends(get_db)):
    token = credentials.raw_token
    session = db.query(Session).filter(Session.token == token).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    db.delete(session)
    db.commit()
    return {"message": "User successfully logged out"}

@router.post("/logout_all", tags=["Users"])
def logout_all_user_sessions(credentials: JwtAuthorizationCredentials = Depends(access_security), db: Session = Depends(get_db)):
    token_data = credentials.get("sub")
    login = token_data.get("login")

    user = db.query(User).filter(User.login == login).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.query(Session).filter(Session.user_id == user.user_id).delete()
    db.commit()
    return {"message": "Logged out from all sessions"}

@router.get("/check_session", tags=["Users"])
def check_session(credentials: JwtAuthorizationCredentials = Depends(access_security)):
    token_data = credentials.get("sub")
    return {
        "message": "Session is active",
        "login": token_data.get("login")
    }

@router.get("/sessions_count", tags=["Users"])
def get_active_sessions_count(
    credentials: JwtAuthorizationCredentials = Depends(access_security),
    db: Session = Depends(get_db),
):
    """
    Получить количество активных сессий текущего пользователя.
    """
    token_data = credentials.get("sub")
    login = token_data.get("login")
    
    user = db.query(User).filter(User.login == login).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    active_sessions_count = db.query(Session).filter(Session.user_id == user.user_id).count()

    return {"active_sessions_count": active_sessions_count}


@router.get("/profile", tags=["Users"])
def get_user_info(credentials: JwtAuthorizationCredentials = Depends(access_security), db: Session = Depends(get_db)):
    token_data = credentials.get("sub")
    login = token_data.get("login")

    user = db.query(User).filter(User.login == login).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"name_first": user.name_first, "name_last": user.name_last, "email": user.mail}

@router.put("/update", tags=["Users"])
def update_user_data(
    user_data: UserUpdateData,
    credentials: JwtAuthorizationCredentials = Depends(access_security),
    db: Session = Depends(get_db),
):
    token_data = credentials.get("sub")
    login = token_data.get("login")
    
    user = db.query(User).filter(User.login == login).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user_data.name_first:
        user.name_first = user_data.name_first
    if user_data.name_last:
        user.name_last = user_data.name_last
    if user_data.mail:
        existing_user = db.query(User).filter(User.mail == user_data.mail).first()
        if existing_user and existing_user.user_id != user.user_id:
            raise HTTPException(status_code=400, detail="Email is already in use")
        user.mail = user_data.mail
    if user_data.login:
        existing_user = db.query(User).filter(User.login == user_data.login).first()
        if existing_user and existing_user.user_id != user.user_id:
            raise HTTPException(status_code=400, detail="Login is already in use")
        user.login = user_data.login

    db.commit()
    db.refresh(user)

    return {"message": "User data updated successfully", "updated_user": {
        "name_first": user.name_first,
        "name_last": user.name_last,
        "mail": user.mail,
        "login": user.login
    }}

@router.get("/export/all_transactions")  # Экспорт всех транзакций
def export_all_transactions(export_request: ExportRequest, db: Session = Depends(get_db)):
    """
    Экспортирует все транзакции пользователя.

    Параметры:
    - export_request: Данные для экспорта.
    - db: Сессия базы данных.

    Возвращает:
    - Файл в нужном формате.
    """
    query = db.query(Transaction).filter(Transaction.user_id == export_request.user_id)
    transactions = query.all()

    # Формируем ответ в нужном формате
    if export_request.format == "json":
        return export_transactions_to_json(transactions)
    
    elif export_request.format == "csv":
        return export_transactions_to_csv({None: transactions}, filename="all_transactions")
    
    elif export_request.format == "excel":
        return export_transactions_to_excel({None: transactions}, filename="all_transactions")
    
    elif export_request.format == "pdf":
        return export_transactions_to_pdf(transactions, filename="transactions_report")
    
    else:
        raise HTTPException(status_code=400, detail="Invalid format")

@router.get("/export/filtered_transactions")  # Экспорт транзакций с фильтрами
def export_filtered_transactions(export_request: ExportRequest, db: Session = Depends(get_db)):
    """
    Экспортирует транзакции пользователя с фильтрами по датам, категории, цели или кредиту.

    Параметры:
    - export_request: Данные для экспорта.
    - db: Сессия базы данных.

    Возвращает:
    - Файл в нужном формате.
    """
    query = db.query(Transaction).filter(Transaction.user_id == export_request.user_id)

    # Применяем фильтры на основе запроса
    if export_request.start_date:
        query = query.filter(Transaction.date >= export_request.start_date)
    if export_request.end_date:
        query = query.filter(Transaction.date <= export_request.end_date)
    if export_request.category:
        query = query.filter(Transaction.category == export_request.category)
    if export_request.target_id:
        query = query.filter(Transaction.target_id == export_request.target_id)
    if export_request.credit_id:
        query = query.filter(Transaction.credit_id == export_request.credit_id)

    transactions = query.all()

    # Формируем ответ в нужном формате
    if export_request.format == "json":
        return export_transactions_to_json(transactions)
    
    elif export_request.format == "csv":
        return export_transactions_to_csv({None: transactions}, filename="filtered_transactions")
    
    elif export_request.format == "excel":
        return export_transactions_to_excel({None: transactions}, filename="filtered_transactions")
    
    elif export_request.format == "pdf":
        return export_transactions_to_pdf(transactions, filename="filtered_transactions_report")
    
    else:
        raise HTTPException(status_code=400, detail="Invalid format")

@router.get("/export/transactions_by_target")  # Экспорт транзакций по целям
def export_transactions_by_target(export_request: ExportRequest, db: Session = Depends(get_db)):
    """
    Экспортирует транзакции пользователя, разделенные по целям.

    Параметры:
    - export_request: Данные для экспорта.
    - db: Сессия базы данных.

    Возвращает:
    - Файл в нужном формате.
    """
    query = db.query(Transaction).filter(Transaction.user_id == export_request.user_id)

    if export_request.target_id:
        target_ids = export_request.target_id if isinstance(export_request.target_id, list) else [export_request.target_id]
        query = query.filter(Transaction.target_id.in_(target_ids))

    transactions_by_target = {}
    transactions = query.all()
    
    # Группируем транзакции по target_id
    for transaction in transactions:
        target_id = transaction.target_id
        if target_id not in transactions_by_target:
            transactions_by_target[target_id] = []
        transactions_by_target[target_id].append(transaction)

    # Формируем ответ в нужном формате
    if export_request.format == "json":
        return export_transactions_to_json(transactions_by_target)
    
    elif export_request.format == "csv":
        return export_transactions_to_csv(transactions_by_target, filename="transactions_by_target")
    
    elif export_request.format == "excel":
        return export_transactions_to_excel(transactions_by_target, filename="transactions_by_target")
    
    elif export_request.format == "pdf":
        return export_transactions_to_pdf(transactions, filename="transactions_by_target_report")
    
    else:
        raise HTTPException(status_code=400, detail="Invalid format")

@router.get("/export/transactions_by_credit")  # Экспорт транзакций по кредитам
def export_transactions_by_credit(export_request: ExportRequest, db: Session = Depends(get_db)):
    """
    Экспортирует транзакции пользователя, разделенные по кредитам.

    Параметры:
    - export_request: Данные для экспорта.
    - db: Сессия базы данных.

    Возвращает:
    - Файл в нужном формате.
    """
    query = db.query(Transaction).filter(Transaction.user_id == export_request.user_id)

    if export_request.credit_id:
        credit_ids = export_request.credit_id if isinstance(export_request.credit_id, list) else [export_request.credit_id]
        query = query.filter(Transaction.credit_id.in_(credit_ids))

    transactions_by_credit = {}
    transactions = query.all()
    
    # Группируем транзакции по credit_id
    for transaction in transactions:
        credit_id = transaction.credit_id
        if credit_id not in transactions_by_credit:
            transactions_by_credit[credit_id] = []
        transactions_by_credit[credit_id].append(transaction)

    # Формируем ответ в нужном формате
    if export_request.format == "json":
        return export_transactions_to_json(transactions_by_credit, filename="trasaction__by_credit")
    
    elif export_request.format == "csv":
        return export_transactions_to_csv(transactions_by_credit, filename="transactions_by_credit")
    
    elif export_request.format == "excel":
        return export_transactions_to_excel(transactions_by_credit, filename="transactions_by_credit")
    
    elif export_request.format == "pdf":
        return export_transactions_to_pdf(transactions, filename="transactions_by_credit_report")
    
    else:
        raise HTTPException(status_code=400, detail="Invalid format")
