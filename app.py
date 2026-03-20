import asyncio
from fastapi import FastAPI, BackgroundTasks, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import os
from evaluation_bot import run_evaluation
from checkin_bot import run_checkin
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

from pydantic import BaseModel
from typing import Optional

class Credentials(BaseModel):
    username: str
    password: str

# Store logs in memory for the UI to poll
logs = []

def ui_logger(message: str):
    print(message)
    logs.append(message)
    if len(logs) > 100:
        logs.pop(0)

class BotStatus:
    is_running = False
    current_task = None
    last_error = None

status = BotStatus()

@app.get("/api/logs")
async def get_logs():
    return {"logs": logs}

@app.get("/api/status")
async def get_status():
    return {
        "is_running": status.is_running,
        "current_task": status.current_task,
        "last_error": status.last_error
    }

def run_automation_task(task_type: str, creds: Credentials):
    status.is_running = True
    status.current_task = task_type
    status.last_error = None
    ui_logger(f"Starting {task_type} for user {creds.username}...")
    
    try:
        if task_type == "evaluation":
            success = run_evaluation(
                username=creds.username, 
                password=creds.password, 
                keep_browser_open=False, 
                logger=ui_logger
            )
        elif task_type == "checkin":
            success = run_checkin(
                username=creds.username, 
                password=creds.password, 
                logger=ui_logger
            )
        else:
            success = False
            ui_logger(f"Unknown task type: {task_type}")
        
        if success:
            ui_logger(f"{task_type.capitalize()} completed successfully.")
        else:
            ui_logger(f"{task_type.capitalize()} failed.")
            status.last_error = f"{task_type.capitalize()} failed."
    except Exception as e:
        ui_logger(f"Error during {task_type}: {e}")
        status.last_error = str(e)
    finally:
        status.is_running = False
        status.current_task = None

@app.post("/api/start/{task_type}")
async def start_task(task_type: str, creds: Credentials, background_tasks: BackgroundTasks):
    if status.is_running:
        return JSONResponse(content={"error": "A task is already running"}, status_code=400)
    
    if task_type not in ["evaluation", "checkin"]:
        return JSONResponse(content={"error": "Invalid task type"}, status_code=400)
    
    logs.clear()
    background_tasks.add_task(run_automation_task, task_type, creds)
    return {"message": f"{task_type.capitalize()} started"}

# Serve Frontend
if not os.path.exists("static"):
    os.makedirs("static")

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_index():
    with open("static/index.html", "r") as f:
        return f.read()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
