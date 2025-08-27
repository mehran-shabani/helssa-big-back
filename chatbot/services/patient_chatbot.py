"""
سرویس چت‌بات بیمار
Patient Chatbot Service
"""

from typing import Dict, List, Optional, Any
from .base_chatbot import BaseChatbotService
from .ai_integration import AIIntegrationService


class PatientChatbotService(BaseChatbotService):
    """
    سرویس چت‌بات اختصاصی بیماران
    """
    
    def __init__(self, user):
        """
        مقداردهی اولیه سرویس چت‌بات بیمار
        
        Args:
            user: کاربر بیمار
        """
        super().__init__(user, 'patient')
        self.ai_service = AIIntegrationService('patient')
    
    def process_message(self, message: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        پردازش پیام بیمار
        
        Args:
            message: پیام بیمار
            context: زمینه اضافی
            
        Returns:
            Dict: پاسخ پردازش شده
        """
        # ذخیره پیام کاربر
        user_message = self.save_user_message(message)
        
        # دریافت تاریخچه مکالمه
        conversation_history = self.get_conversation_history(10)
        
        # پردازش با AI
        ai_response = self.ai_service.process_message(
            message=message,
            context=context,
            conversation_history=conversation_history
        )
        
        # ذخیره پاسخ ربات
        bot_message = self.save_bot_message(
            content=ai_response['content'],
            message_type=ai_response.get('message_type', 'text'),
            response_data=ai_response.get('response_data', {}),
            ai_confidence=ai_response.get('ai_confidence'),
            processing_time=ai_response.get('processing_time')
        )
        
        # بروزرسانی زمینه جلسه
        self._update_patient_context(ai_response, context)
        
        return {
            'response': ai_response,
            'user_message_id': str(user_message.id),
            'bot_message_id': str(bot_message.id),
            'conversation_id': str(self.current_conversation.id),
            'session_id': str(self.current_session.id)
        }
    
    def get_quick_replies(self, context: Optional[Dict] = None) -> List[Dict]:
        """
        دریافت پاسخ‌های سریع برای بیمار
        
        Args:
            context: زمینه فعلی
            
        Returns:
            List[Dict]: فهرست پاسخ‌های سریع
        """
        base_replies = [
            {'title': 'علائم من چیست؟', 'payload': 'symptoms_check'},
            {'title': 'اطلاعات دارو', 'payload': 'medication_info'},
            {'title': 'رزرو نوبت', 'payload': 'book_appointment'},
            {'title': 'تماس با پزشک', 'payload': 'contact_doctor'}
        ]
        
        # پاسخ‌های زمینه‌محور
        if context:
            if context.get('has_symptoms'):
                base_replies.extend([
                    {'title': 'علائم تشدید شده', 'payload': 'symptoms_worsened'},
                    {'title': 'علائم بهبود یافته', 'payload': 'symptoms_improved'}
                ])
            
            if context.get('has_medication'):
                base_replies.extend([
                    {'title': 'عوارض دارو', 'payload': 'medication_side_effects'},
                    {'title': 'زمان مصرف', 'payload': 'medication_timing'}
                ])
        
        return base_replies
    
    def start_symptom_assessment(self) -> Dict[str, Any]:
        """
        شروع ارزیابی علائم
        
        Returns:
            Dict: سؤالات ارزیابی اولیه
        """
        # تغییر نوع مکالمه به بررسی علائم
        if self.current_conversation:
            self.current_conversation.conversation_type = 'symptom_check'
            self.current_conversation.save()
        
        return {
            'content': 'برای ارزیابی بهتر وضعیت شما، لطفاً به سؤالات زیر پاسخ دهید:',
            'message_type': 'text',
            'response_data': {
                'assessment_questions': [
                    {
                        'id': 'main_symptom',
                        'question': 'اصلی‌ترین علامت شما چیست؟',
                        'type': 'multiple_choice',
                        'options': [
                            'درد',
                            'تب',
                            'سردرد',
                            'تهوع',
                            'خستگی',
                            'سایر'
                        ]
                    },
                    {
                        'id': 'symptom_duration',
                        'question': 'این علائم چه مدت است که شروع شده؟',
                        'type': 'multiple_choice',
                        'options': [
                            'کمتر از یک روز',
                            '۱-۳ روز',
                            '۴-۷ روز',
                            'بیشتر از یک هفته'
                        ]
                    },
                    {
                        'id': 'symptom_severity',
                        'question': 'شدت علائم چگونه است؟',
                        'type': 'scale',
                        'scale': {'min': 1, 'max': 10, 'labels': {'1': 'خفیف', '10': 'شدید'}}
                    }
                ]
            }
        }
    
    def process_symptom_response(self, responses: Dict) -> Dict[str, Any]:
        """
        پردازش پاسخ‌های ارزیابی علائم
        
        Args:
            responses: پاسخ‌های بیمار
            
        Returns:
            Dict: تحلیل و توصیه‌ها
        """
        # ذخیره پاسخ‌ها در زمینه
        self._update_session_context({
            'symptom_assessment': responses,
            'assessment_completed_at': str(timezone.now())
        })
        
        # تحلیل پاسخ‌ها
        analysis = self._analyze_symptom_responses(responses)
        
        return {
            'content': analysis['message'],
            'message_type': 'text',
            'response_data': {
                'analysis': analysis,
                'recommendations': analysis.get('recommendations', []),
                'urgency_level': analysis.get('urgency_level', 'normal'),
                'quick_replies': self._get_symptom_followup_replies(analysis)
            }
        }
    
    def request_appointment(self, specialty: str = None, preferred_time: str = None) -> Dict[str, Any]:
        """
        درخواست نوبت
        
        Args:
            specialty: تخصص مورد نیاز
            preferred_time: زمان ترجیحی
            
        Returns:
            Dict: اطلاعات نوبت‌گیری
        """
        # تغییر نوع مکالمه
        if self.current_conversation:
            self.current_conversation.conversation_type = 'appointment'
            self.current_conversation.save()
        
        # ذخیره درخواست در زمینه
        self._update_session_context({
            'appointment_request': {
                'specialty': specialty,
                'preferred_time': preferred_time,
                'requested_at': str(timezone.now())
            }
        })
        
        return {
            'content': 'درخواست نوبت شما دریافت شد. لطفاً اطلاعات تکمیلی را ارائه دهید:',
            'message_type': 'text',
            'response_data': {
                'appointment_form': {
                    'specialty_options': [
                        'پزشک عمومی',
                        'متخصص داخلی',
                        'قلب و عروق',
                        'ارتوپدی',
                        'روانپزشک',
                        'زنان و زایمان'
                    ],
                    'time_slots': [
                        'صبح (۸-۱۲)',
                        'عصر (۱۴-۱۸)',
                        'شب (۱۸-۲۱)'
                    ]
                },
                'quick_replies': [
                    {'title': 'تأیید درخواست', 'payload': 'confirm_appointment'},
                    {'title': 'تغییر زمان', 'payload': 'change_time'},
                    {'title': 'انصراف', 'payload': 'cancel_appointment'}
                ]
            }
        }
    
    def _analyze_symptom_responses(self, responses: Dict) -> Dict[str, Any]:
        """
        تحلیل پاسخ‌های علائم
        
        Args:
            responses: پاسخ‌های بیمار
            
        Returns:
            Dict: تحلیل علائم
        """
        main_symptom = responses.get('main_symptom', '')
        duration = responses.get('symptom_duration', '')
        severity = int(responses.get('symptom_severity', 5))
        
        # تعیین سطح فوریت
        urgency_level = 'normal'
        if severity >= 8 or main_symptom in ['تب بالا', 'درد قفسه سینه']:
            urgency_level = 'high'
        elif severity >= 6:
            urgency_level = 'medium'
        
        # تولید پیام بر اساس تحلیل
        if urgency_level == 'high':
            message = 'بر اساس علائم ذکر شده، توصیه می‌شود در اسرع وقت با پزشک مراجعه کنید.'
            recommendations = [
                'مراجعه فوری به پزشک',
                'در صورت تشدید علائم، به اورژانس مراجعه کنید',
                'داروهای مسکن را بدون نظر پزشک مصرف نکنید'
            ]
        elif urgency_level == 'medium':
            message = 'علائم شما نیاز به بررسی پزشک دارد. توصیه می‌شود طی ۲-۳ روز آینده مراجعه کنید.'
            recommendations = [
                'رزرو نوبت پزشک',
                'استراحت کافی داشته باشید',
                'مایعات زیادی بنوشید'
            ]
        else:
            message = 'علائم شما خفیف به نظر می‌رسد. می‌توانید ابتدا مراقبت‌های خانگی را امتحان کنید.'
            recommendations = [
                'استراحت کافی',
                'مصرف مایعات فراوان',
                'در صورت تداوم یا تشدید علائم، با پزشک مشورت کنید'
            ]
        
        return {
            'message': message,
            'urgency_level': urgency_level,
            'recommendations': recommendations,
            'severity_score': severity,
            'main_symptom': main_symptom,
            'duration': duration
        }
    
    def _get_symptom_followup_replies(self, analysis: Dict) -> List[Dict]:
        """
        دریافت پاسخ‌های پیگیری علائم
        
        Args:
            analysis: تحلیل علائم
            
        Returns:
            List[Dict]: پاسخ‌های پیگیری
        """
        base_replies = [
            {'title': 'رزرو نوبت', 'payload': 'book_appointment'},
            {'title': 'اطلاعات بیشتر', 'payload': 'more_info'}
        ]
        
        if analysis.get('urgency_level') == 'high':
            base_replies.insert(0, {'title': 'تماس اورژانس', 'payload': 'emergency_contact'})
        
        return base_replies
    
    def _update_patient_context(self, ai_response: Dict, context: Optional[Dict]):
        """
        بروزرسانی زمینه بیمار
        
        Args:
            ai_response: پاسخ AI
            context: زمینه فعلی
        """
        updates = {
            'last_interaction': str(timezone.now()),
            'last_category': ai_response.get('category'),
            'confidence_score': ai_response.get('ai_confidence')
        }
        
        if context:
            updates.update(context)
        
        self._update_session_context(updates)