from . import models
from app import schemas
from sqlalchemy import func
from sqlalchemy.orm import Session
from datetime import datetime, date 
from typing import Optional

def get_transactions(db: Session, skip: int = 0, limit: int = 100):
    """
    Retrieve all transaction recorrds from the database.
    """
    return db.query(models.Transaction).order_by(models.Transaction.date.desc()).offset(skip).limit(limit).all()

def create_transaction(db: Session, transaction: schemas.TransactionCreate):
    """
    Create a new transaction record in the database.
    """
    # Create a new SQLAlchemy model instance from schema data
    db_transaction = models.Transaction(**transaction.model_dump())

    # Add instance to the session
    db.add(db_transaction)

    # Commit change
    db.commit()

    # Refresh instance to get new data from DB
    db.refresh(db_transaction)
    return db_transaction

def get_monthly_expense_summary(db: Session):
    """
    Calculates total expenses per category for the current month.
    """
    today = date.today()
    start_of_month = today.replace(day=1)

    # Query the database, grouping by category and summing the amount
    summary = db.query(
        models.Transaction.category,
        func.sum(models.Transaction.amount).label('total_amount')
    ).filter(
        models.Transaction.type == 'Expense',
        func.date(models.Transaction.date) >= start_of_month
    ).group_by(
        models.Transaction.category
    ).all()

    return summary

def get_categories(db: Session, type: Optional[str] = None):
    query = db.query(models.Category)
    if type:
        query = query.filter(models.Category.type == type)
    return query.order_by(models.Category.name).all()

def create_category(db: Session, category: schemas.CategoryCreate):
    """
    Creates a new category in the database.
    Checks for duplicates based on both name and type.
    """
    # Check if a category with the same name AND type already exists
    db_category = db.query(models.Category).filter(
        models.Category.name == category.name,
        models.Category.type == category.type
    ).first()

    if db_category:
        return db_category
    
    db_category = models.Category(**category.model_dump())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

def get_accounts(db: Session):
    return db.query(models.Account).order_by(models.Account.name).all()

def create_account(db: Session, account: schemas.AccountCreate):
    db_account = db.query(models.Account).filter(models.Account.name == account.name).first()
    if db_account:
        return db_account
    db_account = models.Account(**account.model_dump())
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account

def delete_transaction(db: Session, transaction_id: int):
    db_transaction = db.query(models.Transaction).filter(models.Transaction.id == transaction_id).first()
    if db_transaction:
        db.delete(db_transaction)
        db.commit()
    return db_transaction
