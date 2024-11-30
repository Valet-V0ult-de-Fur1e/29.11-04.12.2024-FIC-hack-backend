from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from models import Target as TargetModel
from schemas import Target, TargetCreate
from utils.dependencies import get_db

router = APIRouter()

######### TARGET #########

@router.post("/", response_model=Target, tags=["Targets"])
def add_target(target_data: TargetCreate, db: Session = Depends(get_db)):
    """
    Создает новую цель.

    Параметры:
    - target_data (TargetData): Данные для создания цели.
    - db (Session): Сессия базы данных.

    Возвращает:
    - Созданную цель.
    """
    target = TargetModel(**target_data.dict())
    db.add(target)
    db.commit()
    db.refresh(target)
    return target

@router.put("/{target_id}", response_model=Target, tags=["Targets"])
def edit_target(target_id: int, target_data: TargetCreate, db: Session = Depends(get_db)):
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
    target = db.query(TargetModel).filter(TargetModel.target_id == target_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="Target not found")
    for key, value in target_data.dict().items():
        setattr(target, key, value)
    db.commit()
    db.refresh(target)
    return target

@router.delete("/{target_id}", tags=["Targets"])
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
    target = db.query(TargetModel).filter(TargetModel.target_id == target_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="Target not found")
    db.delete(target)
    db.commit()
    return {"detail": "Target deleted"}

######### END TARGET #########