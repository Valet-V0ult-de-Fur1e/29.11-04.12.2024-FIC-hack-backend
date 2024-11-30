from sqlalchemy.orm import Session
from models import SessionLocal

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