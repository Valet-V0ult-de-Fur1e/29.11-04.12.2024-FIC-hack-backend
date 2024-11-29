from pydantic import BaseModel
import datetime

class TransactionBase(BaseModel):
    user_id: int
    amount: float
    category: str
    date: datetime.date
    type: str
    target_id: int = None
    credit_id: int = None

class TransactionCreate(TransactionBase):
    pass

class Transaction(TransactionBase):
    transaction_id: int

    class Config:
        from_attributes = True

class CreditBase(BaseModel):
    user_id: int
    name: str
    comment: str = None
    amount: float
    procent: float
    date_start: datetime.date
    date_end_plan: datetime.date
    date_end_fact: datetime.date = None
    type: str

class CreditCreate(CreditBase):
    pass

class Credit(CreditBase):
    credit_id: int

    class Config:
        from_attributes = True

class TargetBase(BaseModel):
    user_id: int
    name: str
    comment: str = None
    amount: float
    date_start: datetime.date
    date_end: datetime.date

class TargetCreate(TargetBase):
    pass

class Target(TargetBase):
    target_id: int

    class Config:
        from_attributes = True 