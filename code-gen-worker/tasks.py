import os
from celery import Celery
import time

# Use the same Redis broker as the MCP
redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
celery_app = Celery("tasks", broker=redis_url, backend=redis_url)

@celery_app.task(name="generate_app_task")
def generate_app_task(project_id: str, prompt: str):
    """
    A placeholder task for Jules to implement.
    This task will contain the full agentic loop.
    """
    print(f"Deva Worker: Received task for project {project_id} with prompt: '{prompt}'")
    # Simulate work
    time.sleep(10)
    print(f"Deva Worker: Task for project {project_id} complete.")
    # In the future, this will update the MCP database.
    return {"status": "COMPLETE", "project_id": project_id}