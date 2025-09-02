import os
import time
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from celery import Celery
from sqlmodel import Field, Session, SQLModel, create_engine, select

# --- Database Setup ---
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable not set for worker")

engine = create_engine(DATABASE_URL)

def get_session():
    with Session(engine) as session:
        yield session

# --- Models (must match mcp-server) ---
class Status(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class Project(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: UUID = Field(default_factory=uuid4, index=True, unique=True, nullable=False)
    status: Status = Field(default=Status.PENDING)
    prompt: str
    access_url: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

# --- Celery Setup ---
redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
celery_app = Celery("tasks", broker=redis_url, backend=redis_url)

@celery_app.task(name="generate_app_task")
def generate_app_task(project_id: int, prompt: str):
    """
    This task receives a project ID, updates its status to IN_PROGRESS,
    and will eventually contain the full agentic loop.
    """
    print(f"Worker: Received task for project {project_id} with prompt: '{prompt}'")

    session_generator = get_session()
    session = next(session_generator)
    try:
        # Step 1: Update status to IN_PROGRESS
        print(f"Worker: Updating project {project_id} status to IN_PROGRESS.")
        project = session.get(Project, project_id)
        if not project:
            print(f"Error: Project with id {project_id} not found.")
            return

        project.status = Status.IN_PROGRESS
        project.updated_at = datetime.utcnow()
        session.add(project)
        session.commit()
        session.refresh(project)
        print(f"Worker: Project {project_id} status updated successfully.")

        # Step 2: Simulate the agentic work
        print(f"Worker: Starting generation for project {project_id}...")
        time.sleep(10) # Placeholder for the actual work
        print(f"Worker: Finished generation for project {project_id}.")

    finally:
        session.close()

    return {"status": "Work initiated", "project_id": project_id}