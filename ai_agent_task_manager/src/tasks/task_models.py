"""Task models and management"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class TaskStatus(str, Enum):
    """وضعیت‌های مختلف یک وظیفه"""
    PENDING = "pending"          # در انتظار
    ASSIGNED = "assigned"        # تخصیص داده شده
    IN_PROGRESS = "in_progress"  # در حال انجام
    COMPLETED = "completed"      # تکمیل شده
    FAILED = "failed"           # شکست خورده
    BLOCKED = "blocked"         # مسدود شده
    CANCELLED = "cancelled"     # لغو شده


class TaskPriority(str, Enum):
    """اولویت وظایف"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class TaskDependency(BaseModel):
    """وابستگی بین وظایف"""
    task_id: str
    dependency_type: str = "finish_to_start"  # نوع وابستگی


class Task(BaseModel):
    """مدل اصلی وظیفه"""
    id: str
    title: str
    description: str
    type: str  # نوع وظیفه (gather_requirements, debug_code, etc.)
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.MEDIUM
    complexity: int = Field(ge=1, le=10, default=5)
    
    # Agent مربوطه
    assigned_agent_id: Optional[str] = None
    suggested_agent_type: Optional[str] = None
    
    # زمان‌بندی
    created_at: datetime = Field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    estimated_duration: Optional[int] = None  # به دقیقه
    
    # وابستگی‌ها
    dependencies: List[TaskDependency] = []
    
    # نتایج و خروجی
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    
    # متادیتا
    metadata: Dict[str, Any] = {}
    
    class Config:
        use_enum_values = True
    
    def can_start(self, completed_tasks: List[str]) -> bool:
        """بررسی اینکه آیا وظیفه می‌تواند شروع شود"""
        if self.status != TaskStatus.PENDING:
            return False
        
        # بررسی وابستگی‌ها
        for dep in self.dependencies:
            if dep.task_id not in completed_tasks:
                return False
        
        return True
    
    def to_agent_format(self) -> Dict[str, Any]:
        """تبدیل به فرمت مناسب برای Agent"""
        return {
            "id": self.id,
            "type": self.type,
            "description": self.description,
            "complexity": self.complexity,
            "metadata": self.metadata
        }


class TaskBatch(BaseModel):
    """دسته‌ای از وظایف مرتبط"""
    id: str
    name: str
    description: str
    tasks: List[Task] = []
    created_at: datetime = Field(default_factory=datetime.now)
    
    def add_task(self, task: Task) -> None:
        """اضافه کردن وظیفه به دسته"""
        self.tasks.append(task)
    
    def get_ready_tasks(self, completed_tasks: List[str]) -> List[Task]:
        """دریافت وظایف آماده اجرا"""
        ready = []
        for task in self.tasks:
            if task.can_start(completed_tasks):
                ready.append(task)
        return ready
    
    def get_task_by_id(self, task_id: str) -> Optional[Task]:
        """یافتن وظیفه با ID"""
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None


class TaskTemplate(BaseModel):
    """قالب برای ایجاد وظایف مشابه"""
    id: str
    name: str
    description: str
    type: str
    default_complexity: int = 5
    default_priority: TaskPriority = TaskPriority.MEDIUM
    required_metadata_fields: List[str] = []
    suggested_agent_type: str
    
    def create_task(self, title: str, description: str, **kwargs) -> Task:
        """ایجاد وظیفه از روی قالب"""
        task_id = f"{self.id}_{datetime.now().timestamp()}"
        
        return Task(
            id=task_id,
            title=title,
            description=description,
            type=self.type,
            complexity=kwargs.get("complexity", self.default_complexity),
            priority=kwargs.get("priority", self.default_priority),
            suggested_agent_type=self.suggested_agent_type,
            metadata=kwargs.get("metadata", {})
        )