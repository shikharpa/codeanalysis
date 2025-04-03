from sqlmodel import SQLModel, Field
from typing import Optional
from sqlalchemy import JSON, Column  
from uuid import uuid4
from datetime import datetime


class BaseModel(SQLModel):
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    user_id: str = Field(foreign_key="user.id", nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class User(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    email: str = Field(unique=True, nullable=False, index=True)
    password: str = Field(nullable=False)  # Should be stored as a hashed password
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class Repository(BaseModel, table=True):
    repo_url: str = Field(nullable=False, unique=True, index=True)
    summary: Optional[dict] = Field(default=None, sa_column=Column(JSON, nullable=True))


class Analysis(BaseModel, table=True):
    repo_id: str = Field(foreign_key="repository.id", nullable=False, index=True)
    method_name: str = Field(nullable=False)
    description: str = Field(nullable=False)
    time_complexity: Optional[str] = None
    space_complexity: Optional[str] = None


class Suggestion(BaseModel, table=True):
    repo_id: str = Field(foreign_key="repository.id", nullable=False, index=True)
    analysis_id: str = Field(foreign_key="analysis.id", nullable=False, index=True)
    suggestion: str = Field(nullable=False)