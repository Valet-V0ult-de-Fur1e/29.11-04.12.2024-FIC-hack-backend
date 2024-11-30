from pydantic import BaseModel, EmailStr
import datetime


class UserBase(BaseModel):
    user_id: int
    login: str
    main: EmailStr
    name_first: str
    name_last: str
    password: str


class UserSignInData(BaseModel):
    login: str
    mail: EmailStr
    name_first: str
    name_last: str
    password: str
    host_name: str


class UserLoginData(BaseModel):
    identifier: str  # логин или почта
    password: str
    host_name: str


class UserUpdateData(BaseModel):
    login: str = None
    mail: EmailStr = None
    name_first: str = None
    name_last: str = None


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



class ExportRequest(BaseModel):
    user_id: int
    format: str  # Например, json, csv, excel
    start_date: datetime.date = None
    end_date: datetime.date = None
    category: str = None
    target_id: int = None
    credit_id: int = None

    class Config:
        min_anystr_length = 1
        anystr_strip_whitespace = True