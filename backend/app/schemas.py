from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# Base schema with fields common to both creating and reading transactions
class TransactionBase(BaseModel):
    type: str
    amount: float
    category: str
    description: Optional[str] = None
    from_account: Optional[str] = None
    to_account: Optional[str] = None

# Schema for new transaction
class TransactionCreate(TransactionBase):
    pass

# Schema for reading transaction
# Includes fields that are generated by the database
class Transaction(TransactionBase):
    id: int
    date: datetime

    # This tells Pydantic to read the data even if it's not a dict
    # but an ORM model (SQLAlchemy model)
    class Config:
        from_attributes = True

class CategoryBase(BaseModel):
    name: str
    type: str

class CategoryCreate(CategoryBase):
    pass

class Category(CategoryBase):
    id: int
    class Config:
        from_attributes = True

class AccountBase(BaseModel):
    name: str

class AccountCreate(AccountBase):
    pass

class Account(AccountBase):
    id: int
    class Config:
        from_attributes = True
