from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import mysql.connector
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

app = FastAPI()

# Database configuration
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "task_manager")
}

# Initialize DB connection
try:
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)  # dictionary=True returns rows as dicts
except mysql.connector.Error as e:
    print("Database connection failed:", e)
    raise

# Pydantic model
class Task(BaseModel):
    user_id: int
    title: str
    status: str
    deadline: str

# Create Task
@app.post("/tasks")
def create_task(task: Task):
    try:
        cursor.execute(
            "INSERT INTO tasks (user_id, title, status, deadline) VALUES (%s, %s, %s, %s)",
            (task.user_id, task.title, task.status, task.deadline)
        )
        conn.commit()
        return {"message": "Task created"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# Read all Tasks
@app.get("/tasks")
def get_tasks():
    cursor.execute("SELECT * FROM tasks")
    tasks = cursor.fetchall()
    return tasks

# Update Task
@app.put("/tasks/{task_id}")
def update_task(task_id: int, task: Task):
    try:
        cursor.execute(
            "UPDATE tasks SET title=%s, status=%s, deadline=%s WHERE task_id=%s",
            (task.title, task.status, task.deadline, task_id)
        )
        conn.commit()
        return {"message": "Task updated"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# Delete Task
@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    try:
        cursor.execute("DELETE FROM tasks WHERE task_id=%s", (task_id,))
        conn.commit()
        return {"message": "Task deleted"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# Home route
@app.get("/")
def read_root():
    return {"message": "Welcome to the Task Manager API!"}
