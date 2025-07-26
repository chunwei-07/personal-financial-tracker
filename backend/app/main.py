from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import models
from database.session import engine

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

# --- API Endpoints ---
@app.get("/")
def read_root():
    """A simple endpoint to check if the server is running."""
    return {"message": "Welcome to the Financial Tracker API!"}