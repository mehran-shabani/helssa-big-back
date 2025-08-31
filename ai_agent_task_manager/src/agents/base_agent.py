"""Base Agent class for all AI agents"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime


class AgentType(str, Enum):
    """انواع مختلف Agent ها"""
    COLLECTOR = "collector"  # جمع‌آوری اطلاعات
    DEBUGGER = "debugger"    # دیباگ و رفع باگ
    DEVELOPER = "developer"  # توسعه و کدنویسی
    TESTER = "tester"        # تست و QA
    DOCUMENTER = "documenter"  # مستندسازی
    REVIEWER = "reviewer"    # بازبینی کد
    ARCHITECT = "architect"  # طراحی معماری
    OPTIMIZER = "optimizer"  # بهینه‌سازی


class AgentCapability(BaseModel):
    """قابلیت‌های هر Agent"""
    name: str
    description: str
    complexity_level: int = Field(ge=1, le=10)  # سطح پیچیدگی
    required_tools: List[str] = []


class AgentStatus(str, Enum):
    """وضعیت Agent"""
    IDLE = "idle"
    WORKING = "working"
    WAITING = "waiting"
    ERROR = "error"
    COMPLETED = "completed"


class BaseAgent(ABC, BaseModel):
    """کلاس پایه برای همه Agent ها"""
    id: str
    name: str
    type: AgentType
    capabilities: List[AgentCapability]
    status: AgentStatus = AgentStatus.IDLE
    current_task_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        use_enum_values = True
    
    @abstractmethod
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """اجرای یک وظیفه"""
        pass
    
    @abstractmethod
    async def validate_task(self, task: Dict[str, Any]) -> bool:
        """بررسی اینکه آیا Agent می‌تواند این وظیفه را انجام دهد"""
        pass
    
    def can_handle_task(self, task_type: str, complexity: int) -> bool:
        """بررسی توانایی Agent برای انجام وظیفه"""
        for capability in self.capabilities:
            if capability.name == task_type and capability.complexity_level >= complexity:
                return True
        return False
    
    def estimate_time(self, task: Dict[str, Any]) -> int:
        """تخمین زمان مورد نیاز برای انجام وظیفه (به دقیقه)"""
        base_time = task.get("complexity", 1) * 10
        return base_time