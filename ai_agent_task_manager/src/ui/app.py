"""FastAPI application for the UI"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.orchestrator.task_orchestrator import TaskOrchestrator
from src.tasks.task_models import TaskStatus, TaskPriority

app = FastAPI(title="AI Agent Task Manager", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize orchestrator
orchestrator = TaskOrchestrator()


class ProblemRequest(BaseModel):
    description: str


class TaskAssignmentRequest(BaseModel):
    task_id: str
    agent_id: str


@app.get("/", response_class=HTMLResponse)
async def root():
    """صفحه اصلی"""
    with open("src/ui/index.html", "r", encoding="utf-8") as f:
        return f.read()


@app.post("/api/analyze-problem")
async def analyze_problem(request: ProblemRequest):
    """تحلیل مشکل و ایجاد وظایف"""
    batch = orchestrator.analyze_problem(request.description)
    
    return {
        "batch_id": batch.id,
        "name": batch.name,
        "tasks": [
            {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "type": task.type,
                "status": task.status,
                "priority": task.priority,
                "complexity": task.complexity,
                "suggested_agent_type": task.suggested_agent_type,
                "dependencies": [dep.task_id for dep in task.dependencies]
            }
            for task in batch.tasks
        ]
    }


@app.get("/api/agents")
async def get_agents():
    """دریافت لیست Agent ها"""
    agents = []
    for agent in orchestrator.agents.values():
        agents.append({
            "id": agent.id,
            "name": agent.name,
            "type": agent.type,
            "status": agent.status,
            "capabilities": [
                {
                    "name": cap.name,
                    "description": cap.description,
                    "complexity_level": cap.complexity_level
                }
                for cap in agent.capabilities
            ]
        })
    return {"agents": agents}


@app.get("/api/batches/{batch_id}/ready-tasks")
async def get_ready_tasks(batch_id: str):
    """دریافت وظایف آماده برای تخصیص"""
    tasks = orchestrator.get_ready_tasks(batch_id)
    
    ready_tasks = []
    for task in tasks:
        # پیشنهاد Agent مناسب
        suggested_agent = orchestrator.suggest_agent_for_task(task)
        
        ready_tasks.append({
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "type": task.type,
            "complexity": task.complexity,
            "priority": task.priority,
            "suggested_agent": {
                "id": suggested_agent.id,
                "name": suggested_agent.name,
                "type": suggested_agent.type
            } if suggested_agent else None
        })
    
    return {"ready_tasks": ready_tasks}


@app.post("/api/assign-task")
async def assign_task(request: TaskAssignmentRequest):
    """تخصیص وظیفه به Agent"""
    success = await orchestrator.assign_task_to_agent(
        request.task_id,
        request.agent_id
    )
    
    if not success:
        raise HTTPException(
            status_code=400,
            detail="امکان تخصیص وظیفه به این Agent وجود ندارد"
        )
    
    return {"status": "success", "message": "وظیفه با موفقیت تخصیص داده شد"}


@app.get("/api/batches/{batch_id}/progress")
async def get_batch_progress(batch_id: str):
    """دریافت پیشرفت batch"""
    progress = orchestrator.get_task_progress(batch_id)
    
    if not progress:
        raise HTTPException(status_code=404, detail="Batch not found")
    
    return progress


@app.get("/api/batches/{batch_id}/tasks")
async def get_batch_tasks(batch_id: str):
    """دریافت تمام وظایف یک batch"""
    batch = orchestrator.task_batches.get(batch_id)
    
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    
    tasks = []
    for task in batch.tasks:
        task_data = {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "type": task.type,
            "status": task.status,
            "priority": task.priority,
            "complexity": task.complexity,
            "assigned_agent_id": task.assigned_agent_id,
            "suggested_agent_type": task.suggested_agent_type,
            "dependencies": [dep.task_id for dep in task.dependencies],
            "created_at": task.created_at.isoformat() if task.created_at else None,
            "started_at": task.started_at.isoformat() if task.started_at else None,
            "completed_at": task.completed_at.isoformat() if task.completed_at else None,
            "result": task.result,
            "error_message": task.error_message
        }
        
        # اضافه کردن اطلاعات Agent
        if task.assigned_agent_id:
            agent = orchestrator.agents.get(task.assigned_agent_id)
            if agent:
                task_data["assigned_agent"] = {
                    "id": agent.id,
                    "name": agent.name,
                    "type": agent.type
                }
        
        tasks.append(task_data)
    
    return {"tasks": tasks}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)