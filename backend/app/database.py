from sqlmodel import SQLModel, create_engine, Session
import os

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)

def init_db():
    """Initialize the database by creating all tables defined in SQLModel models."""
    SQLModel.metadata.create_all(engine)

def get_db():
    """Provide a database session for dependency injection."""
    with Session(engine) as session:
        yield session