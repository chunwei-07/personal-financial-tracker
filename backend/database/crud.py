from . import models
from app import schemas
from sqlalchemy import func
from sqlalchemy.orm import Session
from datetime import datetime, date, timedelta, timezone
from typing import Optional

# --- TRANSACTIONS ---
def get_transactions(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    type: Optional[str] = None,
):
    """
    Retrieve transaction records from the database with optional filtering.
    """
    query = db.query(models.Transaction)

    # Apply filters first
    if start_date:
        query = query.filter(models.Transaction.date >= start_date)
    if end_date:
        # Add 1 day to end_date to make the filter inclusive
        query = query.filter(models.Transaction.date < end_date + timedelta(days=1))
    if type:
        query = query.filter(models.Transaction.type == type)

    # Get the total count before pagination
    total_count = query.count()

    # Get the paginated list of transactions
    transactions = query.order_by(models.Transaction.date.desc()).offset(skip).limit(limit).all()

    return {"total_count": total_count, "transactions": transactions}

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

def delete_transaction(db: Session, transaction_id: int):
    db_transaction = db.query(models.Transaction).filter(models.Transaction.id == transaction_id).first()
    if db_transaction:
        db.delete(db_transaction)
        db.commit()
    return db_transaction


# --- CATEGORIES ---
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


# --- ACCOUNTS ---
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


# --- SUMMARY ---
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


# --- NET WORTH ---
def record_net_worth_snapshot(db: Session):
    """
    Calculates the current total net worth and saves it as a snapshot for today.
    If a snapshot for today already exists, it updates it.
    """
    balances = get_account_balances(db=db)
    total_net_worth = sum(balances.values())
    today = datetime.now(timezone.utc).date()   # Use timezone-aware date

    # Check if an entry for today already exists
    existing_snapshot = db.query(models.NetWorthHistory).filter(func.date(models.NetWorthHistory.date) == today).first()

    if existing_snapshot:
        # Update today's existing snapshot
        existing_snapshot.value = total_net_worth
    else:
        # Create a new snapshot for today
        new_snapshot = models.NetWorthHistory(date=datetime.now(timezone.utc), value=total_net_worth)
        db.add(new_snapshot)

    db.commit()

def get_net_worth_history(db: Session, start_date: Optional[date] = None, end_date: Optional[date] = None):
    """
    Retrieves the historical net worth data, ordered by date.
    """
    query = db.query(models.NetWorthHistory)
    if start_date:
        query = query.filter(models.NetWorthHistory.date >= start_date)
    if end_date:
        query = query.filter(models.NetWorthHistory.date < end_date + timedelta(days=1))

    return query.order_by(models.NetWorthHistory.date).all()


# --- RECURRING TRANSACTIONS ---
def get_recurring_transactions(db: Session):
    return db.query(models.RecurringTransaction).order_by(models.RecurringTransaction.day_of_month).all()

def create_recurring_transaction(db: Session, rec_transaction: schemas.RecurringTransactionCreate):
    rec_data = rec_transaction.model_dump()
    if rec_data['type'] == 'Expense':
        rec_data['to_account'] = None
    elif rec_data['type'] == 'Income':
        rec_data['from_account'] = None
    
    db_rec_transaction = models.RecurringTransaction(**rec_data)
    db.add(db_rec_transaction)
    db.commit()
    db.refresh(db_rec_transaction)
    return db_rec_transaction

def update_recurring_transaction(db: Session, rec_transaction_id: int, rec_transaction: schemas.RecurringTransactionCreate):
    db_rec_transaction = db.query(models.RecurringTransaction).filter(models.RecurringTransaction.id == rec_transaction_id).first()
    if db_rec_transaction:
        rec_data = rec_transaction.model_dump()
        if rec_data['type'] == 'Expense':
            rec_data['to_account'] = None
        elif rec_data['type'] == 'Income':
            rec_data['from_account'] = None

        for key, value in rec_data.items():
            setattr(db_rec_transaction, key, value)
        db.commit()
        db.refresh(db_rec_transaction)
    return db_rec_transaction

def delete_recurring_transaction(db: Session, rec_transaction_id: int):
    db_rec_transaction = db.query(models.RecurringTransaction).filter(models.RecurringTransaction.id == rec_transaction_id).first()
    if db_rec_transaction:
        db.delete(db_rec_transaction)
        db.commit()
    return db_rec_transaction

def process_recurring_transactions(db: Session):
    """
    Checks all recurring transaction rules and creates transactions if they are due.
    """
    today = datetime.now(timezone.utc).date()
    all_rules = db.query(models.RecurringTransaction).all()

    for rule in all_rules:
        # Check if the rule's day has passed in the current month
        if today.day >= rule.day_of_month:
            start_of_month = today.replace(day=1)

            transaction_exists_this_month = db.query(models.Transaction).filter(
                models.Transaction.category == rule.category,
                models.Transaction.type == rule.type,
                func.date(models.Transaction.date) >= start_of_month
            ).first()

            if not transaction_exists_this_month:
                print(f"Processing recurring transaction as it was not found this month: {rule.description}")
                
                # Create the new transaction. We'll set its date to be the rule's day for this month.
                transaction_date = today.replace(day=rule.day_of_month)

                new_transaction = schemas.TransactionCreate(
                    type=rule.type,
                    amount=rule.amount,
                    category=rule.category,
                    description=f"(Recurring) {rule.description}", # Use the special description
                    from_account=rule.from_account,
                    to_account=rule.to_account
                )

                db_transaction = models.Transaction(**new_transaction.model_dump(), date=transaction_date)
                
                db.add(db_transaction)
                db.commit()

