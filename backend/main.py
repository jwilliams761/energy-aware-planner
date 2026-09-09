from fastapi import FastAPI
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime

app = FastAPI()
tasks = []

class TaskCategory(str, Enum):
    SCHOOL = "school"
    CAREER = "career"
    PERSONAL = "personal"


class Task(BaseModel):
    title : str 
    description : str
    category : TaskCategory
    due_at : datetime
    estimated_minutes: int
    cognitive_demand: int = Field(ge=1, le=5)
    completed : bool = False


@app.get("/")
def root():
    return {"message": "Energy-Aware Planner API"}
@app.post("/tasks")
def create_task(task: Task):
    tasks.append(task)
    return {"message": "Task created successfully", "task": task}
@app.get("/tasks")
def get_tasks():
    return tasks