from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional

from database import models, crud
from database.session import SessionLocal, engine
from . import schemas

# Tells SQLAlchemy to create all tables defined in models
models.Base.metadata.create_all(bind=engine)

# Create the FastAPI app instance
app = FastAPI()

# --- CORS Configuration ---
# This is crucial for allowing Vue.js frontend
# to communicate with this backend

origins = [
    "http://localhost:5173",    # The default address for Vite (Vue) dev server
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allows specified origins
    allow_credentials=True,
    allow_methods=["*"],    # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],    # Allows all headers
)

# --- Database Dependencies ---
def get_db():
    """
    FastAPI dependency to get a DB session for each request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- API Endpoints ---
@app.get("/")
def read_root():
    """A simple endpoint to check if the server is running."""
    return {"message": "Welcome to the Financial Tracker API!"}


@app.post('/transactions/', response_model=schemas.Transaction)
def create_new_transaction(transaction: schemas.TransactionCreate, db: Session = Depends(get_db)):
    """
    API endpoint to create a new transaction.
    """
    return crud.create_transaction(db=db, transaction=transaction)


@app.get("/transactions/", response_model=List[schemas.Transaction])
def read_transactions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    API endpoint to retrieve all transactions.
    """
    transactions = crud.get_transactions(db, skip=skip, limit=limit)
    return transactions


@app.get("/transactions/summary/monthly-expenses")
def read_monthly_expense_summary(db: Session = Depends(get_db)):
    """
    API endpoint to get a summary of expenses per category for the current month.
    """
    summary = crud.get_monthly_expense_summary(db=db)
    # Convert to dict for easy use in frontend
    return {item.category: item.total_amount for item in summary}

@app.get("/categories/", response_model=List[schemas.Category])
def read_categories(type: Optional[str] = None, db: Session = Depends(get_db)):
    categories = crud.get_categories(db=db, type=type)
    return categories

@app.post("/categories/", response_model=schemas.Category)
def create_new_category(category: schemas.CategoryCreate, db: Session = Depends(get_db)):
    return crud.create_category(db=db, category=category)

@app.get("/accounts/", response_model=List[schemas.Account])
def read_accounts(db: Session = Depends(get_db)):
    accounts = crud.get_accounts(db=db)
    return accounts

@app.post("/accounts/", response_model=schemas.Account)
def create_new_account(account: schemas.AccountCreate, db: Session = Depends(get_db)):
    return crud.create_account(db=db, account=account)