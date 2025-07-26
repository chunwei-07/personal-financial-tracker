from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from .session import Base

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime(timezone=True), server_default=func.now())
    type = Column(String, nullable=False)    # Expenses, Income, Transfer
    amount = Column(Float, nullable=False)
    category = Column(String, nullable=False)
    description = Column(String)

    # For transfers, money moves from one acc to another
    # For expenses, money moves from one acc to external (to_account = NULL)
    # For income, money moves from external to one acc   (from_account = NULL)
    from_account = Column(String)
    to_account = Column(String)

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    type = Column(String, nullable=False)

class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True,index=True)
    name = Column(String, unique=True, index=True, nullable=False)
