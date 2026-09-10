import sqlite3
from fastapi import FastAPI, HTTPException
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

class TaskUpdate(BaseModel):
    title : str | None = None
    description : str | None = None
    category : TaskCategory | None = None
    due_at : datetime | None = None
    estimated_minutes: int | None = None
    cognitive_demand: int | None = Field(default=None, ge=1, le=5)
    completed : bool | None = None

class WakefulnessCheckIn(BaseModel):
    wakefulness_level: int = Field(ge=1, le=5)
    available_minutes: int = Field(ge=1)

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
@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor .execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    row = cursor.fetchone()
    connection.close()
    if  row is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return dict(row)

@app.patch("/tasks/{task_id}/complete")
def complete_task(task_id: int):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("UPDATE tasks SET completed = 1 WHERE id = ?", (task_id,))
    if cursor.rowcount == 0:
        connection.close()
        raise HTTPException(status_code=404, detail="Task not found")
    connection.commit()
    connection.close()
    return {"message": "Task marked as completed"}

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    if cursor.rowcount == 0:
        connection.close()
        raise HTTPException(status_code=404, detail="Task not found")
    connection.commit()
    connection.close()
    return {"message": "Task deleted successfully"}

@app.patch("/tasks/{task_id}")
def update_task(task_id: int, task_update: TaskUpdate):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    row = cursor.fetchone()
    if row is None:
        connection.close()
        raise HTTPException(status_code=404, detail="Task not found")
    
    updated_task = {**dict(row), **task_update.model_dump(exclude_unset=True, mode ="json")}

    cursor.execute(
        "UPDATE tasks SET title = ?, description = ?, category = ?, due_at = ?, estimated_minutes = ?, cognitive_demand = ?, completed = ? WHERE id = ?",
        (updated_task["title"], updated_task["description"], updated_task["category"], updated_task["due_at"], updated_task["estimated_minutes"], updated_task["cognitive_demand"], int(updated_task["completed"]), task_id)
    )
    connection.commit()
    connection.close()
    return {"message": "Task updated successfully", "task": updated_task}

@app.post("/recommendations")
def get_recommendations(check_in: WakefulnessCheckIn):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(
        "SELECT * FROM tasks WHERE completed = 0 AND estimated_minutes <= ? AND cognitive_demand <= ? ORDER BY due_at ASC",
        (check_in.available_minutes, check_in.wakefulness_level)
    )
    rows = cursor.fetchall()
    connection.close()
    return [dict(row) for row in rows]