from fastapi.middleware.cors import CORSMiddleware
from multiprocessing.dummy import connection
import sqlite3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime
from sqlite3 import connect 

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials =True,
    allow_methods=["*"],
    allow_headers=["*"]
)

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

def calculate_urgency(due_at: datetime):
    now = datetime.now()
    time_remaining = (due_at - now)
    days_remaining = time_remaining.days

    if days_remaining <= 0:
        return 50
    elif days_remaining <= 1:
        return 45
    elif days_remaining <= 3:
        return 35
    elif days_remaining <= 7:
        return 25
    else:
        return 10


def calculate_category_score(category: str):
    if category == "school":
        return 30
    elif category == "career":
        return 20
    elif category == "personal":
        return 10
    else:
        return 0

def calculate_wakefulness_fit(wakefulness_level: int, cognitive_demand: int):
    difference = (wakefulness_level - cognitive_demand)
    if difference == 0:
        return 20
    elif difference == 1:
        return 15
    elif difference == 2:
        return 10
    else:
        return 5


def generate_recommendation_reason(task, check_in):
    due_at = datetime.fromisoformat(task["due_at"])
    now = datetime.now()
    time_remaining = due_at - now
    days_remaining = time_remaining.days
    if due_at < now:
        urgency_reason = "This task is overdue."
    elif days_remaining <= 1:
        urgency_reason = "This task is due within a day."
    elif days_remaining <= 3:
        urgency_reason = "This task is due within 3 days."
    elif days_remaining <= 7:
        urgency_reason = "This task is due within 7 days."
    else:
        urgency_reason = "This task is due in more than a week."

    if task["category"] == "school":
        category_reason = "This task is a school task, which has a higher priority."
    elif task["category"] == "career":
        category_reason = "This task is a career task, which has a moderate priority."
    else:
        category_reason = "This task is a personal task, which has a lower priority."

    difference = (check_in.wakefulness_level - task["cognitive_demand"])
    if difference == 0:
        wakefulness_reason = "This task closely matches your current wakefulness level."
    elif difference == 1:
        wakefulness_reason = "This task is slightly below your current wakefulness level."
    elif difference == 2:
        wakefulness_reason =  "This task is comfortably within your current wakefulness level."
    else:
        wakefulness_reason  = "This task requires much less cognitive demand than your current wakefulness level allows."

    return category_reason +" " + urgency_reason +" " + wakefulness_reason




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
    cursor.execute("SELECT * FROM tasks")
    tasks = cursor.fetchall()
    connection.close()
    return tasks
    


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

    if check_in.wakefulness_level == 1:
        cursor.execute("SELECT * FROM tasks WHERE completed = 0" )
        all_unfinished_rows = cursor.fetchall()
        urgent_tasks = []        

        for row in all_unfinished_rows:
            task = dict(row)
            due_at = datetime.fromisoformat(task["due_at"])
            urgency_score = calculate_urgency(due_at)
            if urgency_score >= 35:
                urgent_tasks.append(task)
        if urgent_tasks:
            best_task = max(urgent_tasks, key=lambda task: calculate_category_score(task["category"]))
            reason = ("This task is urgent, but your current wakefulness is very low. "
                      "Wash your face if helpful, check your wakefulness again, and return "
                    "to the task if your alertness has improved."
            )
            connection.close()
            return {"reccomentdation_type": "recovery_then_task", "recommended_task": best_task, "reason": reason}
        else:
            return {"reccomentdation_type": "reccomended_task", "recommended_task": None, "reason": "..."}

    if check_in.wakefulness_level == 2:
        cursor.execute("SELECT  * FROM tasks WHERE completed = 0 AND estimated_minutes <= ? AND cognitive_demand <= 2",  
                       (check_in.available_minutes,))
        level_two_rows = cursor.fetchall()
        urgent_level_two_tasks = []
        for row in level_two_rows:
            task = dict(row)
            due_at = datetime.fromisoformat(task["due_at"])
            urgency_score = calculate_urgency(due_at)
            if urgency_score >= 35:
                urgent_level_two_tasks.append(task)
        if urgent_level_two_tasks:
            scored_level_two_tasks = []
            for task in urgent_level_two_tasks:

                wakefulness_score = calculate_wakefulness_fit(check_in.wakefulness_level, task["cognitive_demand"])

                urgency_score = calculate_urgency(datetime.fromisoformat(task["due_at"]))

                category_score = calculate_category_score(task["category"])

                total_score = urgency_score + category_score + wakefulness_score

                scored_level_two_tasks.append((task, total_score))

                best_task = max(scored_level_two_tasks, key=lambda item: item[1])

                reason = generate_recommendation_reason(best_task[0], check_in)

                connection.close()

                return {"reccomendation_type": "reccomended_task", "recommended_task": best_task[0], "score": best_task[1], "reason": reason}
        else:
            connection.close()
            return {"reccomendation_type": "rest", "recommended_task": None, "reason": "Your wakefulness is low and there are no urgent low-demand tasks that need immediate attention. Consider taking a short rest or refreshing break, then check in again."}

            

    cursor.execute(
        "SELECT * FROM tasks WHERE completed = 0 AND estimated_minutes <= ? AND cognitive_demand <= ? ORDER BY due_at ASC",
        (check_in.available_minutes, check_in.wakefulness_level)
    )
    rows = cursor.fetchall()
    connection.close()
    
    scored_tasks = []

    for row in rows:
        task = dict(row)
        due_at = datetime.fromisoformat(task["due_at"])
        urgency_score = calculate_urgency(due_at)
        category_score = calculate_category_score(task["category"])
        wakefulness_score = calculate_wakefulness_fit(check_in.wakefulness_level, task["cognitive_demand"])
        total_score = urgency_score + category_score + wakefulness_score
        scored_tasks.append((task, total_score))
    if not scored_tasks:
        return {"message": "No suitable tasks found"}
    best_task = max(scored_tasks, key=lambda item: item[1])

    reason = generate_recommendation_reason(best_task[0], check_in)

    return {"recommended_task": best_task[0], "score": best_task[1], "reason": reason}
      
    
        
