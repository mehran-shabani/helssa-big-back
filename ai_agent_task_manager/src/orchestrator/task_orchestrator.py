"""Task Orchestrator - هماهنگ کننده اصلی وظایف"""
from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncio
from ..agents.base_agent import BaseAgent, AgentType, AgentStatus
from ..agents.specialized_agents import (
    CollectorAgent, DebuggerAgent, DeveloperAgent, TesterAgent
)
from ..tasks.task_models import Task, TaskBatch, TaskStatus, TaskPriority
import uuid


class TaskOrchestrator:
    """هماهنگ کننده اصلی برای تقسیم و مدیریت وظایف بین Agent ها"""
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.task_batches: Dict[str, TaskBatch] = {}
        self.completed_tasks: List[str] = []
        self._initialize_agents()
    
    def _initialize_agents(self):
        """ایجاد Agent های پیش‌فرض"""
        # Agent جمع‌آوری اطلاعات
        collector = CollectorAgent(id="agent_collector_1", name="جمع‌آوری کننده اصلی")
        self.agents[collector.id] = collector
        
        # Agent دیباگر
        debugger = DebuggerAgent(id="agent_debugger_1", name="دیباگر اصلی")
        self.agents[debugger.id] = debugger
        
        # Agent توسعه‌دهنده
        developer = DeveloperAgent(id="agent_developer_1", name="توسعه‌دهنده اصلی")
        self.agents[developer.id] = developer
        
        # Agent تستر
        tester = TesterAgent(id="agent_tester_1", name="تستر اصلی")
        self.agents[tester.id] = tester
    
    def analyze_problem(self, problem_description: str) -> TaskBatch:
        """تحلیل مشکل و تقسیم آن به وظایف کوچکتر"""
        batch_id = str(uuid.uuid4())
        batch = TaskBatch(
            id=batch_id,
            name="حل مشکل: " + problem_description[:50],
            description=problem_description
        )
        
        # Phase 1: جمع‌آوری اطلاعات
        gather_task = Task(
            id=f"task_{uuid.uuid4()}",
            title="جمع‌آوری اطلاعات و شناسایی مشکلات",
            description="بررسی کامل مشکل و جمع‌آوری تمام اطلاعات مورد نیاز",
            type="gather_requirements",
            priority=TaskPriority.HIGH,
            complexity=7,
            suggested_agent_type=AgentType.COLLECTOR
        )
        batch.add_task(gather_task)
        
        # Phase 2: تحلیل و دیباگ
        analyze_task = Task(
            id=f"task_{uuid.uuid4()}",
            title="تحلیل مشکلات شناسایی شده",
            description="بررسی دقیق مشکلات و یافتن ریشه آنها",
            type="debug_code",
            priority=TaskPriority.HIGH,
            complexity=8,
            suggested_agent_type=AgentType.DEBUGGER,
            dependencies=[{"task_id": gather_task.id, "dependency_type": "finish_to_start"}]
        )
        batch.add_task(analyze_task)
        
        # Phase 3: توسعه راه‌حل
        develop_task = Task(
            id=f"task_{uuid.uuid4()}",
            title="پیاده‌سازی راه‌حل‌ها",
            description="توسعه و پیاده‌سازی راه‌حل‌های مناسب",
            type="implement_feature",
            priority=TaskPriority.MEDIUM,
            complexity=8,
            suggested_agent_type=AgentType.DEVELOPER,
            dependencies=[{"task_id": analyze_task.id, "dependency_type": "finish_to_start"}]
        )
        batch.add_task(develop_task)
        
        # Phase 4: تست
        test_task = Task(
            id=f"task_{uuid.uuid4()}",
            title="تست راه‌حل‌های پیاده‌سازی شده",
            description="اجرای تست‌های کامل برای اطمینان از صحت راه‌حل",
            type="run_tests",
            priority=TaskPriority.MEDIUM,
            complexity=6,
            suggested_agent_type=AgentType.TESTER,
            dependencies=[{"task_id": develop_task.id, "dependency_type": "finish_to_start"}]
        )
        batch.add_task(test_task)
        
        self.task_batches[batch_id] = batch
        return batch
    
    def suggest_agent_for_task(self, task: Task) -> Optional[BaseAgent]:
        """پیشنهاد بهترین Agent برای انجام وظیفه"""
        best_agent = None
        best_score = 0
        
        for agent in self.agents.values():
            # بررسی وضعیت Agent
            if agent.status != AgentStatus.IDLE:
                continue
            
            # بررسی توانایی انجام وظیفه
            if agent.type.value == task.suggested_agent_type:
                score = 10
            else:
                score = 0
            
            # بررسی قابلیت‌ها
            if agent.can_handle_task(task.type, task.complexity):
                score += 5
            
            if score > best_score:
                best_score = score
                best_agent = agent
        
        return best_agent
    
    async def assign_task_to_agent(self, task_id: str, agent_id: str) -> bool:
        """تخصیص وظیفه به Agent مشخص شده توسط کاربر"""
        # یافتن وظیفه
        task = None
        batch = None
        for b in self.task_batches.values():
            t = b.get_task_by_id(task_id)
            if t:
                task = t
                batch = b
                break
        
        if not task:
            return False
        
        # یافتن Agent
        agent = self.agents.get(agent_id)
        if not agent:
            return False
        
        # بررسی امکان تخصیص
        if agent.status != AgentStatus.IDLE:
            return False
        
        # تخصیص
        task.assigned_agent_id = agent_id
        task.status = TaskStatus.ASSIGNED
        task.started_at = datetime.now()
        
        # اجرای وظیفه
        asyncio.create_task(self._execute_task(task, agent))
        
        return True
    
    async def _execute_task(self, task: Task, agent: BaseAgent):
        """اجرای وظیفه توسط Agent"""
        try:
            task.status = TaskStatus.IN_PROGRESS
            
            # اجرای وظیفه
            result = await agent.execute_task(task.to_agent_format())
            
            # ثبت نتیجه
            task.result = result
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()
            self.completed_tasks.append(task.id)
            
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error_message = str(e)
            agent.status = AgentStatus.ERROR
    
    def get_task_progress(self, batch_id: str) -> Dict[str, Any]:
        """دریافت وضعیت پیشرفت وظایف"""
        batch = self.task_batches.get(batch_id)
        if not batch:
            return {}
        
        total = len(batch.tasks)
        completed = sum(1 for t in batch.tasks if t.status == TaskStatus.COMPLETED)
        in_progress = sum(1 for t in batch.tasks if t.status == TaskStatus.IN_PROGRESS)
        failed = sum(1 for t in batch.tasks if t.status == TaskStatus.FAILED)
        
        return {
            "batch_id": batch_id,
            "total_tasks": total,
            "completed": completed,
            "in_progress": in_progress,
            "failed": failed,
            "pending": total - completed - in_progress - failed,
            "progress_percentage": (completed / total * 100) if total > 0 else 0
        }
    
    def get_ready_tasks(self, batch_id: str) -> List[Task]:
        """دریافت وظایف آماده برای تخصیص"""
        batch = self.task_batches.get(batch_id)
        if not batch:
            return []
        
        return batch.get_ready_tasks(self.completed_tasks)