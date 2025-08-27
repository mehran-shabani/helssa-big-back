"""
سرویس چت‌بات پزشک
Doctor Chatbot Service
"""

from typing import Dict, List, Optional, Any
from django.utils import timezone
from .base_chatbot import BaseChatbotService
from .ai_integration import AIIntegrationService


class DoctorChatbotService(BaseChatbotService):
    """
    سرویس چت‌بات اختصاصی پزشکان
    """
    
    def __init__(self, user):
        """
        مقداردهی اولیه سرویس چت‌بات پزشک
        
        Args:
            user: کاربر پزشک
        """
        super().__init__(user, 'doctor')
        self.ai_service = AIIntegrationService('doctor')
    
    def process_message(self, message: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        پردازش پیام پزشک
        
        Args:
            message: پیام پزشک
            context: زمینه اضافی
            
        Returns:
            Dict: پاسخ پردازش شده
        """
        # ذخیره پیام کاربر
        user_message = self.save_user_message(message)
        
        # دریافت تاریخچه مکالمه
        conversation_history = self.get_conversation_history(15)
        
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
        self._update_doctor_context(ai_response, context)
        
        return {
            'response': ai_response,
            'user_message_id': str(user_message.id),
            'bot_message_id': str(bot_message.id),
            'conversation_id': str(self.current_conversation.id),
            'session_id': str(self.current_session.id)
        }
    
    def get_quick_replies(self, context: Optional[Dict] = None) -> List[Dict]:
        """
        دریافت پاسخ‌های سریع برای پزشک
        
        Args:
            context: زمینه فعلی
            
        Returns:
            List[Dict]: فهرست پاسخ‌های سریع
        """
        base_replies = [
            {'title': 'راهنمای تشخیص', 'payload': 'diagnosis_guide'},
            {'title': 'پروتکل‌های درمان', 'payload': 'treatment_protocols'},
            {'title': 'تداخلات دارویی', 'payload': 'drug_interactions'},
            {'title': 'مراجع علمی', 'payload': 'medical_references'}
        ]
        
        # پاسخ‌های زمینه‌محور
        if context:
            if context.get('patient_case'):
                base_replies.extend([
                    {'title': 'بررسی کیس', 'payload': 'case_review'},
                    {'title': 'تشخیص احتمالی', 'payload': 'differential_diagnosis'}
                ])
            
            if context.get('medication_query'):
                base_replies.extend([
                    {'title': 'دوزاژ استاندارد', 'payload': 'standard_dosage'},
                    {'title': 'عوارض جانبی', 'payload': 'side_effects'}
                ])
        
        return base_replies
    
    def get_diagnosis_support(self, symptoms: List[str], patient_info: Dict = None) -> Dict[str, Any]:
        """
        دریافت پشتیبانی تشخیصی
        
        Args:
            symptoms: فهرست علائم
            patient_info: اطلاعات بیمار
            
        Returns:
            Dict: راهنمای تشخیصی
        """
        # تغییر نوع مکالمه
        if self.current_conversation:
            self.current_conversation.conversation_type = 'doctor_consultation'
            self.current_conversation.save()
        
        # ذخیره اطلاعات کیس در زمینه
        self._update_session_context({
            'diagnosis_request': {
                'symptoms': symptoms,
                'patient_info': patient_info,
                'requested_at': str(timezone.now())
            }
        })
        
        # تحلیل علائم
        diagnosis_analysis = self._analyze_symptoms_for_diagnosis(symptoms, patient_info)
        
        return {
            'content': 'بر اساس علائم ارائه شده، تشخیص‌های احتمالی زیر پیشنهاد می‌شود:',
            'message_type': 'text',
            'response_data': {
                'differential_diagnoses': diagnosis_analysis['diagnoses'],
                'recommended_tests': diagnosis_analysis['tests'],
                'treatment_options': diagnosis_analysis['treatments'],
                'guidelines': diagnosis_analysis['guidelines'],
                'quick_replies': [
                    {'title': 'آزمایش‌های بیشتر', 'payload': 'additional_tests'},
                    {'title': 'مشاوره تخصصی', 'payload': 'specialist_consult'},
                    {'title': 'پروتکل درمان', 'payload': 'treatment_protocol'}
                ]
            }
        }
    
    def get_medication_info(self, medication_name: str, patient_context: Dict = None) -> Dict[str, Any]:
        """
        دریافت اطلاعات دارویی
        
        Args:
            medication_name: نام دارو
            patient_context: زمینه بیمار
            
        Returns:
            Dict: اطلاعات کامل دارو
        """
        # ذخیره درخواست در زمینه
        self._update_session_context({
            'medication_query': {
                'medication': medication_name,
                'patient_context': patient_context,
                'queried_at': str(timezone.now())
            }
        })
        
        # دریافت اطلاعات دارو
        medication_info = self._get_medication_details(medication_name, patient_context)
        
        return {
            'content': f'اطلاعات دارویی {medication_name}:',
            'message_type': 'text',
            'response_data': {
                'medication_details': medication_info,
                'quick_replies': [
                    {'title': 'تداخلات دارویی', 'payload': f'interactions_{medication_name}'},
                    {'title': 'دوزاژ بالغین', 'payload': f'adult_dosage_{medication_name}'},
                    {'title': 'عوارض جانبی', 'payload': f'side_effects_{medication_name}'},
                    {'title': 'موارد احتیاط', 'payload': f'precautions_{medication_name}'}
                ]
            }
        }
    
    def get_treatment_protocol(self, condition: str, severity: str = 'moderate') -> Dict[str, Any]:
        """
        دریافت پروتکل درمان
        
        Args:
            condition: بیماری یا وضعیت
            severity: شدت (mild, moderate, severe)
            
        Returns:
            Dict: پروتکل درمان
        """
        # ذخیره درخواست در زمینه
        self._update_session_context({
            'treatment_protocol_request': {
                'condition': condition,
                'severity': severity,
                'requested_at': str(timezone.now())
            }
        })
        
        protocol = self._get_treatment_protocol_details(condition, severity)
        
        return {
            'content': f'پروتکل درمان {condition} (شدت: {severity}):',
            'message_type': 'text',
            'response_data': {
                'protocol': protocol,
                'quick_replies': [
                    {'title': 'مرحله بعدی', 'payload': 'next_step'},
                    {'title': 'عوارض احتمالی', 'payload': 'potential_complications'},
                    {'title': 'پیگیری درمان', 'payload': 'treatment_followup'}
                ]
            }
        }
    
    def search_medical_references(self, query: str, specialty: str = None) -> Dict[str, Any]:
        """
        جستجو در مراجع پزشکی
        
        Args:
            query: عبارت جستجو
            specialty: تخصص (اختیاری)
            
        Returns:
            Dict: نتایج جستجو
        """
        # ذخیره جستجو در زمینه
        self._update_session_context({
            'medical_search': {
                'query': query,
                'specialty': specialty,
                'searched_at': str(timezone.now())
            }
        })
        
        search_results = self._search_medical_literature(query, specialty)
        
        return {
            'content': f'نتایج جستجو برای "{query}":',
            'message_type': 'text',
            'response_data': {
                'search_results': search_results,
                'total_results': len(search_results),
                'quick_replies': [
                    {'title': 'جستجوی دقیق‌تر', 'payload': 'refine_search'},
                    {'title': 'مراجع مرتبط', 'payload': 'related_references'},
                    {'title': 'راهنماهای بالینی', 'payload': 'clinical_guidelines'}
                ]
            }
        }
    
    def _analyze_symptoms_for_diagnosis(self, symptoms: List[str], patient_info: Dict = None) -> Dict[str, Any]:
        """
        تحلیل علائم برای تشخیص
        
        Args:
            symptoms: فهرست علائم
            patient_info: اطلاعات بیمار
            
        Returns:
            Dict: تحلیل تشخیصی
        """
        # این بخش باید با پایگاه‌داده پزشکی یا AI API یکپارچه شود
        # در حال حاضر نمونه‌ای ساده ارائه می‌دهیم
        
        common_diagnoses = [
            {
                'name': 'عفونت دستگاه تنفسی فوقانی',
                'probability': 0.7,
                'symptoms_match': ['سردرد', 'تب', 'گلودرد'],
                'severity': 'خفیف تا متوسط'
            },
            {
                'name': 'گاستریت',
                'probability': 0.5,
                'symptoms_match': ['درد شکم', 'تهوع'],
                'severity': 'متوسط'
            }
        ]
        
        recommended_tests = [
            'آزمایش خون کامل (CBC)',
            'CRP و ESR',
            'کشت ادرار (در صورت نیاز)'
        ]
        
        treatment_options = [
            'درمان علامتی',
            'آنتی‌بیوتیک (در صورت تأیید عفونت باکتریال)',
            'مسکن و ضد تب'
        ]
        
        guidelines = [
            'پیگیری بیمار در صورت عدم بهبودی ظرف ۴۸ ساعت',
            'آموزش بیمار در مورد علائم خطر',
            'تجویز استراحت و مصرف مایعات فراوان'
        ]
        
        return {
            'diagnoses': common_diagnoses,
            'tests': recommended_tests,
            'treatments': treatment_options,
            'guidelines': guidelines
        }
    
    def _get_medication_details(self, medication_name: str, patient_context: Dict = None) -> Dict[str, Any]:
        """
        دریافت جزئیات دارو
        
        Args:
            medication_name: نام دارو
            patient_context: زمینه بیمار
            
        Returns:
            Dict: جزئیات دارو
        """
        # نمونه اطلاعات دارویی - باید با پایگاه‌داده دارویی یکپارچه شود
        return {
            'generic_name': medication_name,
            'brand_names': ['نام تجاری ۱', 'نام تجاری ۲'],
            'dosage_forms': ['قرص', 'کپسول', 'شربت'],
            'standard_dosage': {
                'adult': '۵۰۰ میلی‌گرم هر ۸ ساعت',
                'pediatric': '۲۵ میلی‌گرم/کیلوگرم هر ۸ ساعت'
            },
            'contraindications': ['حساسیت به دارو', 'نارسایی کلیوی شدید'],
            'side_effects': ['تهوع', 'سردرد', 'خستگی'],
            'interactions': ['وارفارین', 'دیگوکسین'],
            'pregnancy_category': 'B',
            'monitoring_required': ['تست‌های کبدی', 'تست‌های کلیوی']
        }
    
    def _get_treatment_protocol_details(self, condition: str, severity: str) -> Dict[str, Any]:
        """
        دریافت جزئیات پروتکل درمان
        
        Args:
            condition: بیماری
            severity: شدت
            
        Returns:
            Dict: جزئیات پروتکل
        """
        # نمونه پروتکل درمان - باید با راهنماهای بالینی یکپارچه شود
        return {
            'first_line_treatment': ['دارو A', 'دارو B'],
            'second_line_treatment': ['دارو C', 'دارو D'],
            'duration': '۷-۱۰ روز',
            'monitoring': ['علائم حیاتی', 'پاسخ به درمان'],
            'follow_up': 'بازدید مجدد پس از ۴۸ ساعت',
            'complications_to_watch': ['عارضه A', 'عارضه B'],
            'patient_education': ['نکات مراقبتی', 'علائم خطر']
        }
    
    def _search_medical_literature(self, query: str, specialty: str = None) -> List[Dict]:
        """
        جستجو در متون پزشکی
        
        Args:
            query: عبارت جستجو
            specialty: تخصص
            
        Returns:
            List[Dict]: نتایج جستجو
        """
        # نمونه نتایج - باید با پایگاه‌داده مراجع پزشکی یکپارچه شود
        return [
            {
                'title': f'مقاله مرتبط با {query}',
                'authors': ['نویسنده ۱', 'نویسنده ۲'],
                'journal': 'مجله پزشکی',
                'year': 2023,
                'abstract': 'خلاصه مقاله...',
                'link': 'https://example.com/article1'
            },
            {
                'title': f'راهنمای بالینی {query}',
                'organization': 'انجمن پزشکی',
                'year': 2023,
                'summary': 'خلاصه راهنما...',
                'link': 'https://example.com/guideline1'
            }
        ]
    
    def _update_doctor_context(self, ai_response: Dict, context: Optional[Dict]):
        """
        بروزرسانی زمینه پزشک
        
        Args:
            ai_response: پاسخ AI
            context: زمینه فعلی
        """
        updates = {
            'last_interaction': str(timezone.now()),
            'last_category': ai_response.get('category'),
            'confidence_score': ai_response.get('ai_confidence'),
            'consultation_type': context.get('consultation_type') if context else None
        }
        
        if context:
            updates.update(context)
        
        self._update_session_context(updates)