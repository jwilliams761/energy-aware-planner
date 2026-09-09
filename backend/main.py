import sqlite3
from fastapi import FastAPI
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime
from sqlite3 import connect 

app = FastAPI()

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

def get_db_connection():
    connection = sqlite3.connect("planner.db")
    connection.row_factory = sqlite3.Row
    return connection

def init_db():
    connection= get_db_connection()
    cursor = connection.cursor()
    cursor.execute(""" CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        category TEXT NOT NULL,
        due_at TEXT NOT NULL,
        estimated_minutes INTEGER NOT NULL,
        cognitive_demand INTEGER NOT NULL,
        completed INTEGER NOT NULL DEFAULT 0
        )""")
    connection.commit()
    connection.close()

init_db()

@app.get("/")
def root():
    return {"message": "Energy-Aware Planner API"}
@app.post("/tasks")
def create_task(task: Task):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO tasks (title, description, category, due_at, estimated_minutes, cognitive_demand, completed) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (task.title, task.description, task.category.value, task.due_at.isoformat(), task.estimated_minutes, task.cognitive_demand, int(task.completed))
    )
    connection.commit()
    connection.close()
    return {"message": "Task created successfully", "task": task}
@app.get("/tasks")
def get_tasks():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor .execute("SELECT * FROM tasks")
    rows = cursor.fetchall()
    connection.close()
    return [dict(row) for row in rows]