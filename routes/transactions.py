from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from models import Transaction as TransactionModel
from schemas import Transaction, TransactionCreate
from utils.dependencies import get_db 

router = APIRouter()

######### TRANSACTIONS #########
@router.post("/", response_model=Transaction, tags=["Transactions"])
def add_transaction(transaction_data: TransactionCreate, db: Session = Depends(get_db)):
    """
    Создает новую транзакцию.

    Параметры:
    - transaction_data (TransactionData): Данные для создания транзакции.
    - db (Session): Сессия базы данных.

    Возвращает:
    - Созданную транзакцию.
    """
    transaction = TransactionModel(**transaction_data.dict())
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction

@router.put("/{transaction_id}", response_model=Transaction, tags=["Transactions"])
def edit_transaction(transaction_id: int, transaction_data: TransactionCreate, db: Session = Depends(get_db)):
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
    transaction = db.query(TransactionModel).filter(TransactionModel.transaction_id == transaction_id).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    for key, value in transaction_data.dict().items():
        setattr(transaction, key, value)
    db.commit()
    db.refresh(transaction)
    return transaction

@router.delete("/{transaction_id}", tags=["Transactions"])
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
    transaction = db.query(TransactionModel).filter(TransactionModel.transaction_id == transaction_id).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    db.delete(transaction)
    db.commit()
    return {"detail": "Transaction deleted"}

######### END TRANSACTIONS #########