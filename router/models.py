from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    login = Column(String, unique=True, nullable=False)
    mail = Column(String, unique=True, nullable=False)
    name_first = Column(String, nullable=False)
    name_last = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    sessions = relationship("Session", back_populates="user")
    transactions = relationship("Transaction", back_populates="user")
    credits = relationship("Credit", back_populates="user")
    targets = relationship("Target", back_populates="user")


class Transaction(Base):
    __tablename__ = 'transactions'
    
    transaction_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    amount = Column(Float, nullable=False)
    category = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    type = Column(String, nullable=False)
    target_id = Column(Integer, ForeignKey('targets.target_id'))
    credit_id = Column(Integer, ForeignKey('credits.credit_id'))
    
    user = relationship("User", back_populates="transactions")


class Credit(Base):
    __tablename__ = 'credits'
    
    credit_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    name = Column(String, nullable=False)
    comment = Column(String)
    amount = Column(Float, nullable=False)
    procent = Column(Float, nullable=False)
    date_start = Column(Date, nullable=False)
    date_end_plan = Column(Date, nullable=False)
    date_end_fact = Column(Date)
    type = Column(String, nullable=False)
    
    user = relationship("User", back_populates="credits")


class Session(Base):
    __tablename__ = 'sessions'
    
    user_id = Column(Integer, ForeignKey('users.user_id'), primary_key=True)
    token = Column(String, nullable=False)
    host_name = Column(String, nullable=False)
    date_start = Column(Date, nullable=False)
    
    user = relationship("User", back_populates="sessions")


class Target(Base):
    __tablename__ = 'targets'
    
    target_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    name = Column(String, nullable=False)
    comment = Column(String)
    amount = Column(Float, nullable=False)
    date_start = Column(Date, nullable=False)
    date_end = Column(Date, nullable=False)
    
    user = relationship("User", back_populates="targets")
