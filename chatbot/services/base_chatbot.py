"""
کلاس پایه برای سرویس‌های چت‌بات
Base Chatbot Service
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from django.utils import timezone
from django.contrib.auth import get_user_model
from ..models import ChatbotSession, Conversation, Message, ChatbotResponse

User = get_user_model()


class BaseChatbotService(ABC):
    """
    کلاس پایه برای سرویس‌های چت‌بات
    """
    
    def __init__(self, user: User, session_type: str):
        """
        مقداردهی اولیه سرویس چت‌بات
        
        Args:
            user: کاربر
            session_type: نوع جلسه (patient یا doctor)
        """
        self.user = user
        self.session_type = session_type
        self.current_session: Optional[ChatbotSession] = None
        self.current_conversation: Optional[Conversation] = None
    
    def get_or_create_session(self) -> ChatbotSession:
        """
        دریافت یا ایجاد جلسه فعال
        
        Returns:
            ChatbotSession: جلسه فعال کاربر
        """
        # جستجو برای جلسه فعال موجود
        active_session = ChatbotSession.objects.filter(
            user=self.user,
            session_type=self.session_type,
            status='active'
        ).first()
        
        if active_session and active_session.is_active:
            self.current_session = active_session
        else:
            # ایجاد جلسه جدید
            self.current_session = ChatbotSession.objects.create(
                user=self.user,
                session_type=self.session_type,
                status='active',
                expires_at=timezone.now() + timezone.timedelta(hours=24)
            )
        
        return self.current_session
    
    def get_or_create_conversation(self, conversation_type: str = 'general') -> Conversation:
        """
        دریافت یا ایجاد مکالمه فعال
        
        Args:
            conversation_type: نوع مکالمه
            
        Returns:
            Conversation: مکالمه فعال
        """
        if not self.current_session:
            self.get_or_create_session()
        
        # جستجو برای مکالمه فعال موجود
        active_conversation = self.current_session.conversations.filter(
            is_active=True
        ).first()
        
        if active_conversation:
            self.current_conversation = active_conversation
        else:
            # ایجاد مکالمه جدید
            self.current_conversation = Conversation.objects.create(
                session=self.current_session,
                conversation_type=conversation_type,
                title=self._generate_conversation_title(conversation_type)
            )
        
        return self.current_conversation
    
    def save_user_message(self, content: str, message_type: str = 'text') -> Message:
        """
        ذخیره پیام کاربر
        
        Args:
            content: محتوای پیام
            message_type: نوع پیام
            
        Returns:
            Message: پیام ذخیره شده
        """
        if not self.current_conversation:
            self.get_or_create_conversation()
        
        return Message.objects.create(
            conversation=self.current_conversation,
            sender_type='user',
            message_type=message_type,
            content=content
        )
    
    def save_bot_message(
        self, 
        content: str, 
        message_type: str = 'text',
        response_data: Optional[Dict] = None,
        ai_confidence: Optional[float] = None,
        processing_time: Optional[float] = None
    ) -> Message:
        """
        ذخیره پیام ربات
        
        Args:
            content: محتوای پیام
            message_type: نوع پیام
            response_data: داده‌های پاسخ
            ai_confidence: درجه اطمینان AI
            processing_time: زمان پردازش
            
        Returns:
            Message: پیام ذخیره شده
        """
        if not self.current_conversation:
            self.get_or_create_conversation()
        
        return Message.objects.create(
            conversation=self.current_conversation,
            sender_type='bot',
            message_type=message_type,
            content=content,
            response_data=response_data or {},
            ai_confidence=ai_confidence,
            processing_time=processing_time
        )
    
    def get_conversation_history(self, limit: int = 50) -> List[Message]:
        """
        دریافت تاریخچه مکالمه
        
        Args:
            limit: حداکثر تعداد پیام‌ها
            
        Returns:
            List[Message]: فهرست پیام‌ها
        """
        if not self.current_conversation:
            return []
        
        return list(
            self.current_conversation.messages.order_by('-created_at')[:limit]
        )
    
    def end_conversation(self, summary: str = "") -> None:
        """
        پایان دادن به مکالمه فعال
        
        Args:
            summary: خلاصه مکالمه
        """
        if self.current_conversation:
            self.current_conversation.is_active = False
            if summary:
                self.current_conversation.summary = summary
            self.current_conversation.save()
    
    def end_session(self) -> None:
        """
        پایان دادن به جلسه فعال
        """
        if self.current_session:
            self.current_session.end_session()
    
    @abstractmethod
    def process_message(self, message: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        پردازش پیام کاربر
        
        Args:
            message: پیام کاربر
            context: زمینه اضافی
            
        Returns:
            Dict: پاسخ پردازش شده
        """
        pass
    
    @abstractmethod
    def get_quick_replies(self, context: Optional[Dict] = None) -> List[Dict]:
        """
        دریافت پاسخ‌های سریع
        
        Args:
            context: زمینه
            
        Returns:
            List[Dict]: فهرست پاسخ‌های سریع
        """
        pass
    
    def _generate_conversation_title(self, conversation_type: str) -> str:
        """
        تولید عنوان مکالمه
        
        Args:
            conversation_type: نوع مکالمه
            
        Returns:
            str: عنوان مکالمه
        """
        type_titles = {
            'patient_inquiry': 'استعلام بیمار',
            'doctor_consultation': 'مشاوره پزشک',
            'symptom_check': 'بررسی علائم',
            'medication_info': 'اطلاعات دارو',
            'appointment': 'نوبت‌گیری',
            'general': 'گفتگوی عمومی'
        }
        
        base_title = type_titles.get(conversation_type, 'مکالمه')
        timestamp = timezone.now().strftime('%H:%M')
        return f"{base_title} - {timestamp}"
    
    def _update_session_context(self, context_updates: Dict) -> None:
        """
        بروزرسانی زمینه جلسه
        
        Args:
            context_updates: بروزرسانی‌های زمینه
        """
        if self.current_session:
            self.current_session.context_data.update(context_updates)
            self.current_session.save(update_fields=['context_data', 'last_activity'])