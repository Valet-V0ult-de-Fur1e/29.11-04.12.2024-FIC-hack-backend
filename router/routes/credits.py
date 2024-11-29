from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from models import Credit as CreditModel
from schemas import Credit, CreditCreate
from dependencies import get_db

router = APIRouter()

######### CREDIT #########


@router.post("/", response_model=Credit, tags=["Credits"])
def add_credit(credit_data: CreditCreate, db: Session = Depends(get_db)):
    """
    Создает новый кредит.

    Параметры:
    - credit_data (CreditData): Данные для создания кредита.
    - db (Session): Сессия базы данных.

    Возвращает:
    - Созданный кредит.
    """
    credit = CreditModel(**credit_data.dict())
    db.add(credit)
    db.commit()
    db.refresh(credit)
    return credit

@router.put("/{credit_id}", response_model=Credit, tags=["Credits"])
def edit_credit(credit_id: int, credit_data: CreditCreate, db: Session = Depends(get_db)):
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
    credit = db.query(CreditModel).filter(CreditModel.credit_id == credit_id).first()
    if not credit:
        raise HTTPException(status_code=404, detail="Credit not found")
    for key, value in credit_data.dict().items():
        setattr(credit, key, value)
    db.commit()
    db.refresh(credit)
    return credit

@router.delete("/{credit_id}", tags=["Credits"])
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
    credit = db.query(CreditModel).filter(CreditModel.credit_id == credit_id).first()
    if not credit:
        raise HTTPException(status_code=404, detail="Credit not found")
    db.delete(credit)
    db.commit()
    return {"detail": "Credit deleted"}

######### END CREDIT #########