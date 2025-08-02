from . import models
from app import schemas
from sqlalchemy import func
from sqlalchemy.orm import Session
from datetime import datetime, date , timedelta
from typing import Optional

def get_transactions(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    type: Optional[str] = None,
):
    """
    Retrieve transaction records from the database with optional filtering.
    """
    query = db.query(models.Transaction)

    if start_date:
        query = query.filter(models.Transaction.date >= start_date)
    if end_date:
        # Add 1 day to end_date to make the filter inclusive
        query = query.filter(models.Transaction.date < end_date + timedelta(days=1))
    if type:
        query = query.filter(models.Transaction.type == type)

    return query.order_by(models.Transaction.date.desc()).offset(skip).limit(limit).all()

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

def get_summary_by_category(
    db: Session,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    type: str = "Expense",
):
    """
    Calculates total transaction amounts per category for a given date range and type.
    """
    query = db.query(
        models.Transaction.category,
        func.sum(models.Transaction.amount).label("total_amount"),
    ).filter(models.Transaction.type == type)

    if start_date:
        query = query.filter(models.Transaction.date >= start_date)
    if end_date:
        query = query.filter(models.Transaction.date < end_date + timedelta(days=1))

    summary = query.group_by(models.Transaction.category).all()
    return {item.category: item.total_amount for item in summary}

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

def get_account_balances(db: Session):
    """
    Calculates the current balance for every account.
    Balance = (Sum of all incoming transactions) - (Sum of all outgoing transactions)
    """
    accounts = db.query(models.Account).all()
    balances = {}

    for account in accounts:
        total_in = db.query(func.sum(models.Transaction.amount)).filter(
            models.Transaction.to_account == account.name
        ).scalar() or 0.0

        total_out = db.query(func.sum(models.Transaction.amount)).filter(
            models.Transaction.from_account == account.name
        ).scalar() or 0.0

        balances[account.name] = total_in - total_out

    return balances

def update_account(db: Session, account_id: int, account: schemas.AccountCreate):
    db_account = db.query(models.Account).filter(models.Account.id == account_id).first()
    if db_account:
        db_account.name = account.name
        db.commit()
        db.refresh(db_account)
    return db_account

def delete_account(db: Session, account_id: int):
    db_account = db.query(models.Account).filter(models.Account.id == account_id).first()
    if db_account:
        # Before deleting, check if this account is used in any transactions
        usage_count = db.query(models.Transaction).filter(
            (models.Transaction.from_account == db_account.name) | (models.Transaction.to_account == db_account.name)
        ).count()

        if usage_count > 0:
            return None
        
        db.delete(db_account)
        db.commit()
        return db_account
    return db_account

def update_category(db: Session, category_id: int, category: schemas.CategoryCreate):
    db_category = db.query(models.Category).filter(models.Category.id == category_id).first()
    if db_category:
        db_category.name = category.name
        db_category.type = category.type
        db.commit()
        db.refresh(db_category)
    return db_category

def delete_category(db: Session, category_id: int):
    db_category = db.query(models.Category).filter(models.Category.id == category_id).first()
    if db_category:
        usage_count = db.query(models.Transaction).filter(models.Transaction.category == db_category.name).count()
        if usage_count > 0:
            return None
        
        db.delete(db_category)
        db.commit()
        return db_category
    return db_category

def update_transaction(db: Session, transaction_id: int, transaction: schemas.TransactionCreate):
    """
    Updates an existing transaction in the database.
    """
    db_transaction = db.query(models.Transaction).filter(models.Transaction.id == transaction_id).first()

    if db_transaction:
        # Update the model instance with data from Pydantic schema
        transaction_data = transaction.model_dump()
        for key, value in transaction_data.items():
            setattr(db_transaction, key, value)

        db.commit()
        db.refresh(db_transaction)

    return db_transaction

def get_summary_by_month(
    db: Session,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    type: str = "Expense",
):
    """
    Calculates total transaction amounts per month for a given date range and type.
    """
    query = db.query(
        # Extract Year and Month from the date. SQLite uses strftime.
        func.strftime("%Y-%m", models.Transaction.date).label("month"),
        func.sum(models.Transaction.amount).label("total_amount"),
    ).filter(models.Transaction.type == type)

    if start_date:
        query = query.filter(models.Transaction.date >= start_date)
    if end_date:
        query = query.filter(models.Transaction.date < end_date + timedelta(days=1))

    summary = query.group_by("month").order_by("month").all()
    return {item.month: item.total_amount for item in summary}

