"""
سرویس یکپارچه‌سازی با هوش مصنوعی
AI Integration Service
"""

import time
import logging
from typing import Dict, List, Optional, Any, Tuple
from django.conf import settings
from .response_matcher import ResponseMatcherService

logger = logging.getLogger(__name__)


class AIIntegrationService:
    """
    سرویس یکپارچه‌سازی با خدمات هوش مصنوعی
    """
    
    def __init__(self, user_type: str = 'patient'):
        """
        مقداردهی اولیه
        
        Args:
            user_type: نوع کاربر (patient یا doctor)
        """
        self.user_type = user_type
        self.response_matcher = ResponseMatcherService(target_user=user_type)
    
    def process_message(
        self, 
        message: str, 
        context: Optional[Dict] = None,
        conversation_history: Optional[List] = None
    ) -> Dict[str, Any]:
        """
        پردازش پیام با هوش مصنوعی
        
        Args:
            message: پیام کاربر
            context: زمینه مکالمه
            conversation_history: تاریخچه مکالمه
            
        Returns:
            Dict: پاسخ پردازش شده
        """
        start_time = time.time()
        
        try:
            # تحلیل هدف پیام
            intent_analysis = self.response_matcher.analyze_message_intent(message)
            
            # جستجو برای پاسخ از پیش تعریف شده
            predefined_response = self.response_matcher.find_matching_response(
                message, 
                category=intent_analysis.get('primary_intent')
            )
            
            if predefined_response:
                response = self._format_predefined_response(predefined_response)
                response['ai_confidence'] = 0.9
            else:
                # استفاده از AI برای تولید پاسخ
                response = self._generate_ai_response(
                    message, context, conversation_history, intent_analysis
                )
            
            # محاسبه زمان پردازش
            processing_time = time.time() - start_time
            response['processing_time'] = processing_time
            
            # اضافه کردن تحلیل هدف
            response['intent_analysis'] = intent_analysis
            
            return response
            
        except Exception as e:
            logger.error(f"خطا در پردازش پیام: {str(e)}")
            return self._get_error_response()
    
    def _format_predefined_response(self, response_obj) -> Dict[str, Any]:
        """
        فرمت کردن پاسخ از پیش تعریف شده
        
        Args:
            response_obj: شیء پاسخ
            
        Returns:
            Dict: پاسخ فرمت شده
        """
        return {
            'content': response_obj.response_text,
            'message_type': 'text',
            'response_data': response_obj.response_data,
            'source': 'predefined',
            'category': response_obj.category,
            'ai_confidence': 0.9
        }
    
    def _generate_ai_response(
        self, 
        message: str,
        context: Optional[Dict],
        conversation_history: Optional[List],
        intent_analysis: Dict
    ) -> Dict[str, Any]:
        """
        تولید پاسخ با هوش مصنوعی
        
        Args:
            message: پیام کاربر
            context: زمینه
            conversation_history: تاریخچه
            intent_analysis: تحلیل هدف
            
        Returns:
            Dict: پاسخ تولید شده
        """
        # در حال حاضر از پاسخ‌های ساده استفاده می‌کنیم
        # در آینده می‌توان با API های AI خارجی یکپارچه کرد
        
        if self.user_type == 'patient':
            return self._generate_patient_response(message, intent_analysis)
        else:
            return self._generate_doctor_response(message, intent_analysis)
    
    def _generate_patient_response(self, message: str, intent_analysis: Dict) -> Dict[str, Any]:
        """
        تولید پاسخ برای بیمار
        
        Args:
            message: پیام
            intent_analysis: تحلیل هدف
            
        Returns:
            Dict: پاسخ
        """
        primary_intent = intent_analysis.get('primary_intent')
        
        responses = {
            'symptom_inquiry': {
                'content': 'لطفاً علائم خود را به طور دقیق‌تر شرح دهید. چه زمانی شروع شده و شدت آن چگونه است؟',
                'response_data': {
                    'quick_replies': [
                        {'title': 'درد خفیف', 'payload': 'pain_mild'},
                        {'title': 'درد شدید', 'payload': 'pain_severe'},
                        {'title': 'تب دارم', 'payload': 'fever'},
                        {'title': 'سردرد', 'payload': 'headache'}
                    ]
                }
            },
            'medication_info': {
                'content': 'برای اطلاعات دقیق دارو، لطفاً نام دارو را بنویسید یا عکس جعبه دارو را ارسال کنید.',
                'response_data': {
                    'quick_replies': [
                        {'title': 'نام دارو', 'payload': 'medication_name'},
                        {'title': 'عوارض جانبی', 'payload': 'side_effects'},
                        {'title': 'نحوه مصرف', 'payload': 'dosage'}
                    ]
                }
            },
            'appointment': {
                'content': 'برای رزرو نوبت، لطفاً تخصص مورد نظر و زمان ترجیحی خود را مشخص کنید.',
                'response_data': {
                    'quick_replies': [
                        {'title': 'پزشک عمومی', 'payload': 'general_doctor'},
                        {'title': 'متخصص داخلی', 'payload': 'internal_medicine'},
                        {'title': 'روانپزشک', 'payload': 'psychiatrist'}
                    ]
                }
            }
        }
        
        if primary_intent in responses:
            response = responses[primary_intent].copy()
            response['ai_confidence'] = 0.7
        else:
            response = {
                'content': 'سؤال شما را دریافت کردم. می‌توانید سؤال خود را واضح‌تر بیان کنید تا بتوانم بهتر کمکتان کنم؟',
                'ai_confidence': 0.5,
                'response_data': {
                    'quick_replies': [
                        {'title': 'مشکل سلامتی', 'payload': 'health_issue'},
                        {'title': 'اطلاعات دارو', 'payload': 'medication'},
                        {'title': 'نوبت‌گیری', 'payload': 'appointment'}
                    ]
                }
            }
        
        response.update({
            'message_type': 'text',
            'source': 'ai_generated',
            'category': primary_intent or 'general'
        })
        
        return response
    
    def _generate_doctor_response(self, message: str, intent_analysis: Dict) -> Dict[str, Any]:
        """
        تولید پاسخ برای پزشک
        
        Args:
            message: پیام
            intent_analysis: تحلیل هدف
            
        Returns:
            Dict: پاسخ
        """
        primary_intent = intent_analysis.get('primary_intent')
        
        responses = {
            'symptom_inquiry': {
                'content': 'بر اساس علائم ذکر شده، پیشنهاد می‌کنم موارد زیر را بررسی کنید:',
                'response_data': {
                    'suggestions': [
                        'بررسی علائم حیاتی بیمار',
                        'انجام آزمایش‌های لازم',
                        'در نظر گیری تشخیص‌های افتراقی'
                    ],
                    'quick_replies': [
                        {'title': 'پروتکل درمان', 'payload': 'treatment_protocol'},
                        {'title': 'آزمایش‌های مورد نیاز', 'payload': 'required_tests'},
                        {'title': 'مشاوره تخصصی', 'payload': 'specialist_consult'}
                    ]
                }
            },
            'medication_info': {
                'content': 'اطلاعات دارویی و تداخلات احتمالی:',
                'response_data': {
                    'quick_replies': [
                        {'title': 'دوزاژ استاندارد', 'payload': 'standard_dosage'},
                        {'title': 'تداخلات دارویی', 'payload': 'drug_interactions'},
                        {'title': 'عوارض جانبی', 'payload': 'adverse_effects'}
                    ]
                }
            }
        }
        
        if primary_intent in responses:
            response = responses[primary_intent].copy()
            response['ai_confidence'] = 0.8
        else:
            response = {
                'content': 'چگونه می‌توانم در مورد این موضوع کمکتان کنم؟',
                'ai_confidence': 0.6,
                'response_data': {
                    'quick_replies': [
                        {'title': 'راهنمای تشخیص', 'payload': 'diagnosis_guide'},
                        {'title': 'پروتکل درمان', 'payload': 'treatment_protocol'},
                        {'title': 'مراجع علمی', 'payload': 'references'}
                    ]
                }
            }
        
        response.update({
            'message_type': 'text',
            'source': 'ai_generated',
            'category': primary_intent or 'general'
        })
        
        return response
    
    def _get_error_response(self) -> Dict[str, Any]:
        """
        دریافت پاسخ خطا
        
        Returns:
            Dict: پاسخ خطا
        """
        error_response = self.response_matcher.get_error_response()
        
        if error_response:
            return self._format_predefined_response(error_response)
        
        return {
            'content': 'متأسفانه خطایی در پردازش پیام شما رخ داده است. لطفاً دوباره تلاش کنید.',
            'message_type': 'text',
            'source': 'system',
            'category': 'error',
            'ai_confidence': 1.0
        }
    
    def get_quick_replies_for_context(self, context: Optional[Dict] = None) -> List[Dict]:
        """
        دریافت پاسخ‌های سریع بر اساس زمینه
        
        Args:
            context: زمینه فعلی
            
        Returns:
            List[Dict]: فهرست پاسخ‌های سریع
        """
        if self.user_type == 'patient':
            return [
                {'title': 'علائم من', 'payload': 'my_symptoms'},
                {'title': 'اطلاعات دارو', 'payload': 'medication_info'},
                {'title': 'نوبت‌گیری', 'payload': 'book_appointment'},
                {'title': 'راهنما', 'payload': 'help'}
            ]
        else:
            return [
                {'title': 'راهنمای تشخیص', 'payload': 'diagnosis_guide'},
                {'title': 'پروتکل‌های درمان', 'payload': 'treatment_protocols'},
                {'title': 'مراجع علمی', 'payload': 'medical_references'},
                {'title': 'ابزارهای تشخیصی', 'payload': 'diagnostic_tools'}
            ]