from . import models
from app import schemas
from sqlalchemy import func
from sqlalchemy.orm import Session
from datetime import datetime, date 

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