from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from datetime import date
import os

from database import models, crud
from database.session import SessionLocal, engine
from . import schemas

# Tells SQLAlchemy to create all tables defined in models
models.Base.metadata.create_all(bind=engine)

# Lifespan Function
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    print("Application startup: Seeding database...")
    db = SessionLocal()
    try:
        # Check for default accounts
        default_accounts = ["Bank Account", "Cash", "Touch and Go E-wallet"]
        for acc_name in default_accounts:
            account_exists = db.query(models.Account).filter(models.Account.name == acc_name).first()
            if not account_exists:
                crud.create_account(db, schemas.AccountCreate(name=acc_name))

        # Check for initial balance category
        initial_balance_category_exists = db.query(models.Category).filter(models.Category.name == "Initial Balance").first()
        if not initial_balance_category_exists:
            crud.create_category(db, schemas.CategoryCreate(name="Initial Balance", type="Income"))

        print("Database seeding complete.")
    finally:
        db.close()

    yield

    # Shutdown logic
    print("Application shutdown.")

# Create the FastAPI app instance
app = FastAPI(lifespan=lifespan)

# --- CORS Configuration ---
# This is crucial for allowing Vue.js frontend
# to communicate with this backend

origins = [
    "http://localhost:5173",    # The default address for Vite (Vue) dev server
    "http://127.0.0.1:5173",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
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
# --- TRANSACTIONS ---
@app.post('/transactions/', response_model=schemas.Transaction)
def create_new_transaction(transaction: schemas.TransactionCreate, db: Session = Depends(get_db)):
    """
    API endpoint to create a new transaction.
    """
    return crud.create_transaction(db=db, transaction=transaction)

@app.get("/transactions/", response_model=List[schemas.Transaction])
def read_transactions(
    skip: int = 0,
    limit: int = 100,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    type: Optional[str] = None,
    db: Session = Depends(get_db),
):
    transactions = crud.get_transactions(
        db, skip=skip, limit=limit, start_date=start_date, end_date=end_date, type=type
    )
    return transactions

@app.get("/transactions/summary/by-category", response_model=Dict[str, float])
def read_summary_by_category(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    type: str = "Expense",
    db: Session = Depends(get_db),
):
    summary = crud.get_summary_by_category(
        db=db, start_date=start_date, end_date=end_date, type=type
    )
    return summary

@app.get("/transactions/summary/by-month", response_model=Dict[str, float])
def read_summary_by_month(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    type: str = "Expense",
    db: Session = Depends(get_db),
):
    summary = crud.get_summary_by_month(
        db=db, start_date=start_date, end_date=end_date, type=type
    )
    return summary

@app.put("/transactions/{transaction_id}", response_model=schemas.Transaction)
def update_transaction_by_id(transaction_id: int, transaction: schemas.TransactionCreate, db: Session = Depends(get_db)):
    """
    API endpoint to update existing transaction.
    """
    updated_transaction = crud.update_transaction(db=db, transaction_id=transaction_id, transaction=transaction)
    if updated_transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return updated_transaction

@app.delete("/transactions/{transaction_id}", response_model=schemas.Transaction)
def delete_transaction_by_id(transaction_id: int, db: Session = Depends(get_db)):
    db_transaction = crud.delete_transaction(db=db, transaction_id=transaction_id)
    if db_transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return db_transaction


# --- CATEGORIES ---
@app.get("/categories/", response_model=List[schemas.Category])
def read_categories(type: Optional[str] = None, db: Session = Depends(get_db)):
    categories = crud.get_categories(db=db, type=type)
    return categories

@app.post("/categories/", response_model=schemas.Category)
def create_new_category(category: schemas.CategoryCreate, db: Session = Depends(get_db)):
    return crud.create_category(db=db, category=category)

@app.put("/categories/{category_id}", response_model=schemas.Category)
def update_category_by_id(category_id: int, category: schemas.CategoryCreate, db: Session = Depends(get_db)):
    db_category = crud.update_category(db=db, category_id=category_id, category=category)
    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return db_category

@app.delete("/categories/{category_id}")
def delete_category_by_id(category_id: int, db: Session = Depends(get_db)):
    db_category = crud.delete_category(db=db, category_id=category_id)
    if db_category is None:
        raise HTTPException(status_code=403, detail="Category is in use and cannot be deleted")
    return {"message": "Category deleted successfully"}


# --- ACCOUNTS ---
@app.get("/accounts/", response_model=List[schemas.Account])
def read_accounts(db: Session = Depends(get_db)):
    accounts = crud.get_accounts(db=db)
    return accounts

@app.post("/accounts/", response_model=schemas.Account)
def create_new_account(account: schemas.AccountCreate, db: Session = Depends(get_db)):
    return crud.create_account(db=db, account=account)

@app.put("/accounts/{account_id}", response_model=schemas.Account)
def update_account_by_id(account_id: int, account: schemas.AccountCreate, db: Session = Depends(get_db)):
    db_account = crud.update_account(db=db, account_id=account_id, account=account)
    if db_account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    return db_account

@app.delete("/accounts/{account_id}")
def delete_account_by_id(account_id: int, db: Session = Depends(get_db)):
    db_account = crud.delete_account(db=db, account_id=account_id)
    if db_account is None:
        raise HTTPException(status_code=403, detail="Account is in use and cannot be deleted")
    return {"message": "Account deleted successfully"}

@app.get("/accounts/balances", response_model=Dict[str, float])
def read_account_balances(db: Session = Depends(get_db)):
    """
    API endpoint to retrieve the calculated current balance for all accounts.
    """
    return crud.get_account_balances(db=db)


# Define the path to the frontend build directory
FRONTEND_BUILD_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'frontend', 'dist')

# Mount the 'assets' directory from the build folder
app.mount(
    "/assets",
    StaticFiles(directory=os.path.join(FRONTEND_BUILD_DIR, 'assets')),
    name="assets"
)

@app.get("/{catchall:path}", response_class=FileResponse, include_in_schema=False)
def serve_frontend(catchall: str):
    """
    Catch-all endpoint to serve the frontend's index.html.
    This allows Vue Router to handle routing on the client side.
    """
    # Add a check to avoid trying to serve non-existent files
    file_path = os.path.join(FRONTEND_BUILD_DIR, catchall)
    if os.path.isfile(file_path):
        return FileResponse(file_path)
    
    # If it's not a file, it's a client-side route, serve index.html
    return FileResponse(os.path.join(FRONTEND_BUILD_DIR, 'index.html'))