import os
from contextlib import asynccontextmanager
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Field, Session, SQLModel, create_engine, select
from celery_client import celery_app


# Database Connection
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    # A default for local dev without the .env file, though the .env is preferred.
    DATABASE_URL = "postgresql://mcp_user:supersecretpassword@mcp-db/mcp_database"

engine = create_engine(DATABASE_URL, echo=True)


# Models and Schemas
class Status(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class ProjectBase(SQLModel):
    prompt: str
    access_url: Optional[str] = None

class Project(ProjectBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: UUID = Field(default_factory=uuid4, index=True, unique=True, nullable=False)
    status: Status = Field(default=Status.PENDING)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

class ProjectCreate(ProjectBase):
    pass

class ProjectRead(ProjectBase):
    task_id: UUID
    status: Status
    created_at: datetime
    updated_at: datetime


def get_session():
    with Session(engine) as session:
        yield session

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # On startup
    print("Creating database and tables...")
    create_db_and_tables()
    yield
    # On shutdown
    print("Shutting down...")

app = FastAPI(
    title="MCP Server",
    lifespan=lifespan
)

@app.post("/apps/create", response_model=ProjectRead)
def create_project(project_create: ProjectCreate, session: Session = Depends(get_session)):
    # Create the project record in the database
    db_project = Project.model_validate(project_create)
    session.add(db_project)
    session.commit()
    session.refresh(db_project)

    # Dispatch the generation task to the worker
    # The task name must match the one defined in the worker service
    celery_app.send_task(
        "generate_app_task",
        args=[db_project.id, db_project.prompt]
    )

    return db_project

@app.get("/apps/status/{task_id}", response_model=ProjectRead)
def get_project_status(task_id: UUID, session: Session = Depends(get_session)):
    project = session.exec(select(Project).where(Project.task_id == task_id)).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@app.get("/")
def read_root():
    return {"message": "Master Control Program for Project Genesis is online."}