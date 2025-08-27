"""
تست‌های سیستم چت‌بات
Chatbot Tests
"""

from django.test import TestCase, TransactionTestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from unittest.mock import patch, MagicMock
from datetime import timedelta

from .models import ChatbotSession, Conversation, Message, ChatbotResponse
from .services import PatientChatbotService, DoctorChatbotService, AIIntegrationService
from .serializers import (
    ChatbotSessionSerializer, ConversationSerializer, MessageSerializer,
    SendMessageRequestSerializer
)

User = get_user_model()


class ChatbotModelsTest(TestCase):
    """
    تست‌های مدل‌های چت‌بات
    """
    
    def setUp(self):
        """
        راه‌اندازی اولیه تست‌ها
        """
        self.user = User.objects.create_user(
            phone_number='09123456789',
            first_name='احمد',
            last_name='محمدی'
        )
    
    def test_chatbot_session_creation(self):
        """
        تست ایجاد جلسه چت‌بات
        """
        session = ChatbotSession.objects.create(
            user=self.user,
            session_type='patient',
            status='active'
        )
        
        self.assertEqual(session.user, self.user)
        self.assertEqual(session.session_type, 'patient')
        self.assertEqual(session.status, 'active')
        self.assertTrue(session.is_active)
        self.assertIsNotNone(session.id)
    
    def test_session_expiration(self):
        """
        تست انقضای جلسه
        """
        # جلسه منقضی شده
        expired_session = ChatbotSession.objects.create(
            user=self.user,
            session_type='patient',
            status='active',
            expires_at=timezone.now() - timedelta(hours=1)
        )
        
        self.assertFalse(expired_session.is_active)
    
    def test_conversation_creation(self):
        """
        تست ایجاد مکالمه
        """
        session = ChatbotSession.objects.create(
            user=self.user,
            session_type='patient'
        )
        
        conversation = Conversation.objects.create(
            session=session,
            conversation_type='symptom_check',
            title='بررسی علائم'
        )
        
        self.assertEqual(conversation.session, session)
        self.assertEqual(conversation.conversation_type, 'symptom_check')
        self.assertEqual(conversation.message_count, 0)
    
    def test_message_creation(self):
        """
        تست ایجاد پیام
        """
        session = ChatbotSession.objects.create(
            user=self.user,
            session_type='patient'
        )
        
        conversation = Conversation.objects.create(
            session=session,
            conversation_type='general'
        )
        
        message = Message.objects.create(
            conversation=conversation,
            sender_type='user',
            message_type='text',
            content='سلام، چطور حالم رو بررسی کنم؟'
        )
        
        self.assertEqual(message.conversation, conversation)
        self.assertTrue(message.is_from_user)
        self.assertFalse(message.is_from_bot)
        self.assertEqual(conversation.message_count, 1)
    
    def test_chatbot_response_model(self):
        """
        تست مدل پاسخ چت‌بات
        """
        response = ChatbotResponse.objects.create(
            category='greeting',
            target_user='patient',
            trigger_keywords=['سلام', 'درود'],
            response_text='سلام! چطور می‌توانم کمکتان کنم؟',
            priority=1
        )
        
        self.assertEqual(response.category, 'greeting')
        self.assertEqual(response.target_user, 'patient')
        self.assertTrue(response.is_active)


class ChatbotServicesTest(TestCase):
    """
    تست‌های سرویس‌های چت‌بات
    """
    
    def setUp(self):
        """
        راه‌اندازی اولیه
        """
        self.patient_user = User.objects.create_user(
            phone_number='09123456789',
            first_name='احمد',
            last_name='محمدی'
        )
        
        self.doctor_user = User.objects.create_user(
            phone_number='09987654321',
            first_name='دکتر فاطمه',
            last_name='احمدی'
        )
        
        # ایجاد پاسخ‌های نمونه
        ChatbotResponse.objects.create(
            category='greeting',
            target_user='both',
            trigger_keywords=['سلام', 'hello'],
            response_text='سلام! خوش آمدید.',
            priority=1
        )
    
    def test_patient_chatbot_service(self):
        """
        تست سرویس چت‌بات بیمار
        """
        service = PatientChatbotService(self.patient_user)
        
        # تست ایجاد جلسه
        session = service.get_or_create_session()
        self.assertEqual(session.user, self.patient_user)
        self.assertEqual(session.session_type, 'patient')
        
        # تست ایجاد مکالمه
        conversation = service.get_or_create_conversation()
        self.assertEqual(conversation.session, session)
        
        # تست ذخیره پیام
        user_message = service.save_user_message('سلام')
        self.assertEqual(user_message.sender_type, 'user')
        self.assertEqual(user_message.content, 'سلام')
    
    def test_doctor_chatbot_service(self):
        """
        تست سرویس چت‌بات پزشک
        """
        service = DoctorChatbotService(self.doctor_user)
        
        # تست ایجاد جلسه
        session = service.get_or_create_session()
        self.assertEqual(session.session_type, 'doctor')
        
        # تست پردازش پیام
        result = service.process_message('اطلاعات دارو آسپرین')
        self.assertIn('response', result)
        self.assertIn('user_message_id', result)
        self.assertIn('bot_message_id', result)
    
    def test_ai_integration_service(self):
        """
        تست سرویس یکپارچه‌سازی AI
        """
        ai_service = AIIntegrationService('patient')
        
        # تست پردازش پیام
        response = ai_service.process_message('سردرد دارم')
        
        self.assertIn('content', response)
        self.assertIn('ai_confidence', response)
        self.assertIn('processing_time', response)
        self.assertIsInstance(response['ai_confidence'], float)
    
    def test_symptom_assessment(self):
        """
        تست ارزیابی علائم
        """
        service = PatientChatbotService(self.patient_user)
        assessment = service.start_symptom_assessment()
        
        self.assertIn('content', assessment)
        self.assertIn('response_data', assessment)
        self.assertIn('assessment_questions', assessment['response_data'])
        
        # تست پردازش پاسخ‌های ارزیابی
        responses = {
            'main_symptom': 'سردرد',
            'symptom_duration': '۲ روز',
            'symptom_severity': 7
        }
        
        analysis = service.process_symptom_response(responses)
        self.assertIn('content', analysis)
        self.assertIn('response_data', analysis)


class ChatbotAPITest(APITestCase):
    """
    تست‌های API چت‌بات
    """
    
    def setUp(self):
        """
        راه‌اندازی اولیه API تست‌ها
        """
        self.patient_user = User.objects.create_user(
            phone_number='09123456789',
            first_name='احمد',
            last_name='محمدی'
        )
        
        self.doctor_user = User.objects.create_user(
            phone_number='09987654321',
            first_name='دکتر فاطمه',
            last_name='احمدی'
        )
        
        self.client = APIClient()
    
    def test_patient_start_session_api(self):
        """
        تست API شروع جلسه بیمار
        """
        self.client.force_authenticate(user=self.patient_user)
        
        url = reverse('chatbot:patient-start-session')
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('session', response.data)
        self.assertIn('quick_replies', response.data)
    
    def test_patient_send_message_api(self):
        """
        تست API ارسال پیام بیمار
        """
        self.client.force_authenticate(user=self.patient_user)
        
        # ابتدا جلسه را شروع کن
        start_url = reverse('chatbot:patient-start-session')
        self.client.post(start_url)
        
        # حالا پیام ارسال کن
        send_url = reverse('chatbot:patient-send-message')
        data = {
            'message': 'سردرد دارم',
            'message_type': 'text'
        }
        
        response = self.client.post(send_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('response', response.data)
        self.assertIn('user_message_id', response.data)
        self.assertIn('bot_message_id', response.data)
    
    def test_doctor_diagnosis_support_api(self):
        """
        تست API پشتیبانی تشخیصی پزشک
        """
        self.client.force_authenticate(user=self.doctor_user)
        
        url = reverse('chatbot:doctor-diagnosis-support')
        data = {
            'symptoms': ['سردرد', 'تب', 'گلودرد'],
            'patient_age': 30,
            'patient_gender': 'M'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('content', response.data)
        self.assertIn('response_data', response.data)
    
    def test_unauthorized_access(self):
        """
        تست دسترسی غیرمجاز
        """
        url = reverse('chatbot:patient-start-session')
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_invalid_message_data(self):
        """
        تست داده‌های نامعتبر پیام
        """
        self.client.force_authenticate(user=self.patient_user)
        
        # شروع جلسه
        start_url = reverse('chatbot:patient-start-session')
        self.client.post(start_url)
        
        # ارسال پیام خالی
        send_url = reverse('chatbot:patient-send-message')
        data = {'message': ''}
        
        response = self.client.post(send_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ChatbotSerializersTest(TestCase):
    """
    تست‌های سریالایزرها
    """
    
    def setUp(self):
        """
        راه‌اندازی اولیه
        """
        self.user = User.objects.create_user(
            phone_number='09123456789',
            first_name='احمد',
            last_name='محمدی'
        )
        
        self.session = ChatbotSession.objects.create(
            user=self.user,
            session_type='patient'
        )
    
    def test_session_serializer(self):
        """
        تست سریالایزر جلسه
        """
        serializer = ChatbotSessionSerializer(self.session)
        data = serializer.data
        
        self.assertEqual(data['session_type'], 'patient')
        self.assertIn('user', data)
        self.assertIn('conversation_count', data)
    
    def test_send_message_request_serializer(self):
        """
        تست سریالایزر درخواست ارسال پیام
        """
        data = {
            'message': 'سلام',
            'message_type': 'text'
        }
        
        serializer = SendMessageRequestSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        # تست داده نامعتبر
        invalid_data = {'message': ''}
        invalid_serializer = SendMessageRequestSerializer(data=invalid_data)
        self.assertFalse(invalid_serializer.is_valid())
    
    def test_message_serializer_validation(self):
        """
        تست اعتبارسنجی سریالایزر پیام
        """
        conversation = Conversation.objects.create(
            session=self.session,
            conversation_type='general'
        )
        
        # پیام معتبر
        valid_data = {
            'conversation': conversation.id,
            'sender_type': 'user',
            'content': 'پیام تست'
        }
        
        serializer = MessageSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid())
        
        # پیام خیلی طولانی
        long_message = 'پیام ' * 1000  # بیش از 4000 کاراکتر
        invalid_data = {
            'conversation': conversation.id,
            'sender_type': 'user',
            'content': long_message
        }
        
        invalid_serializer = MessageSerializer(data=invalid_data)
        self.assertFalse(invalid_serializer.is_valid())


class ChatbotMiddlewareTest(TestCase):
    """
    تست‌های middleware چت‌بات
    """
    
    def setUp(self):
        """
        راه‌اندازی اولیه
        """
        self.user = User.objects.create_user(
            phone_number='09123456789',
            first_name='احمد',
            last_name='محمدی'
        )
        self.client = APIClient()
    
    @patch('django.core.cache.cache.get')
    @patch('django.core.cache.cache.set')
    def test_rate_limiting_middleware(self, mock_cache_set, mock_cache_get):
        """
        تست middleware محدودسازی نرخ
        """
        # شبیه‌سازی درخواست‌های زیاد
        mock_cache_get.return_value = [int(timezone.now().timestamp())] * 35
        
        self.client.force_authenticate(user=self.user)
        
        url = reverse('chatbot:patient-send-message')
        data = {'message': 'تست'}
        
        response = self.client.post(url, data, format='json')
        
        # باید محدودیت اعمال شود
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
    
    def test_security_middleware_sensitive_content(self):
        """
        تست middleware امنیتی برای محتوای حساس
        """
        self.client.force_authenticate(user=self.user)
        
        # شروع جلسه
        start_url = reverse('chatbot:patient-start-session')
        self.client.post(start_url)
        
        # ارسال محتوای حساس
        send_url = reverse('chatbot:patient-send-message')
        sensitive_data = {
            'message': 'رمز عبور من 123456 است'
        }
        
        response = self.client.post(send_url, sensitive_data, format='json')
        
        # باید خطای امنیتی بازگرداند
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('محتوای حساس', response.data['message'])