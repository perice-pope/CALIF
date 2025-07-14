from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import uvicorn

# It's good practice to have database session management in a separate file.
from . import database
from .database import engine, SessionLocal

# Import your models here when you have them.
# For now, we define Pydantic models directly.
from pydantic import BaseModel, Field
from datetime import datetime

# Create all tables in the database.
# This is okay for development, but for production, you might want to use Alembic for migrations.
# models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="CALIF API",
    description="Provides access to cross-asset luxury investment signals and indices.",
    version="1.0.0",
)

# --- Pydantic Models ---

class Signal(BaseModel):
    asset_type: str
    last_price: float
    rolling_mean_30d: float
    z_score: float
    is_deal: bool
    updated_at: datetime

    class Config:
        orm_mode = True

class Index(BaseModel):
    # Define your Index model here based on your database schema
    # For example:
    name: str
    value: float
    updated_at: datetime

    class Config:
        orm_mode = True

# --- Dependency ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "Welcome to the CALIF API"}

@app.get("/signals", response_model=List[Signal])
def get_signals(db: Session = Depends(get_db)):
    """
    Retrieve all the latest deal signals from the database.
    """
    # This assumes you have a 'signals' table and a corresponding SQLAlchemy model.
    # We will use raw SQL for now as we don't have the model defined.
    try:
        query = "SELECT asset_type, last_price, rolling_mean_30d, z_score, is_deal, updated_at FROM signals WHERE is_deal = TRUE ORDER BY updated_at DESC"
        results = db.execute(database.text(query)).fetchall()
        return results
    except Exception as e:
        # This will catch issues like "relation 'signals' does not exist" if the table isn't created.
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/index", response_model=List[Index])
def get_index(db: Session = Depends(get_db)):
    """
    Retrieve the computed indices.
    (This is a placeholder and needs a corresponding table and logic).
    """
    # This endpoint is a placeholder. To implement it, you would:
    # 1. Have a service that calculates indices and stores them in a table (e.g., 'indices').
    # 2. Query that table here.
    # For now, it returns a hardcoded example.
    return [
        {"name": "WatchIndex", "value": 1234.56, "updated_at": datetime.utcnow()},
        {"name": "WineIndex", "value": 7890.12, "updated_at": datetime.utcnow()},
    ]

# To run locally for development: `uvicorn api.app:app --reload`
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 