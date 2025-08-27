"""
ویوهای سیستم چت‌بات
Chatbot Views
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db.models import Q
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from .models import ChatbotSession, Conversation, Message, ChatbotResponse
from .serializers import (
    ChatbotSessionSerializer, ConversationSerializer, ConversationListSerializer,
    MessageSerializer, ChatbotResponseSerializer, SendMessageRequestSerializer,
    SendMessageResponseSerializer, StartSessionResponseSerializer,
    SymptomAssessmentRequestSerializer, DiagnosisSupportRequestSerializer,
    MedicationInfoRequestSerializer, AppointmentRequestSerializer,
    ConversationHistorySerializer
)
from .services import PatientChatbotService, DoctorChatbotService

User = get_user_model()


class StandardResultsSetPagination(PageNumberPagination):
    """
    صفحه‌بندی استاندارد
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class BaseChatbotViewSet(viewsets.ModelViewSet):
    """
    کلاس پایه برای ViewSet های چت‌بات
    """
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """
        فیلتر کردن بر اساس کاربر فعلی
        """
        return self.queryset.filter(user=self.request.user)


class PatientChatbotViewSet(viewsets.GenericViewSet):
    """
    API چت‌بات بیماران
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_chatbot_service(self):
        """
        دریافت سرویس چت‌بات بیمار
        """
        return PatientChatbotService(self.request.user)
    
    @extend_schema(
        summary="شروع جلسه چت‌بات بیمار",
        description="ایجاد یا دریافت جلسه فعال چت‌بات برای بیمار",
        responses={200: StartSessionResponseSerializer}
    )
    @action(detail=False, methods=['post'])
    def start_session(self, request):
        """
        شروع جلسه چت‌بات
        """
        try:
            chatbot_service = self.get_chatbot_service()
            session = chatbot_service.get_or_create_session()
            
            # دریافت پیام خوشامدگویی
            ai_response = chatbot_service.ai_service.response_matcher.get_greeting_response()
            greeting_message = None
            
            if ai_response:
                greeting_message = {
                    'content': ai_response.response_text,
                    'message_type': 'text',
                    'response_data': ai_response.response_data
                }
            
            # دریافت پاسخ‌های سریع اولیه
            quick_replies = chatbot_service.get_quick_replies()
            
            return Response({
                'session': ChatbotSessionSerializer(session).data,
                'greeting_message': greeting_message,
                'quick_replies': quick_replies
            })
            
        except Exception as e:
            return Response(
                {'error': f'خطا در شروع جلسه: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @extend_schema(
        summary="ارسال پیام به چت‌بات",
        description="ارسال پیام کاربر و دریافت پاسخ چت‌بات",
        request=SendMessageRequestSerializer,
        responses={200: SendMessageResponseSerializer}
    )
    @action(detail=False, methods=['post'])
    def send_message(self, request):
        """
        ارسال پیام به چت‌بات
        """
        serializer = SendMessageRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            chatbot_service = self.get_chatbot_service()
            
            # پردازش پیام
            result = chatbot_service.process_message(
                message=serializer.validated_data['message'],
                context=serializer.validated_data.get('context')
            )
            
            return Response(result)
            
        except Exception as e:
            return Response(
                {'error': f'خطا در پردازش پیام: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @extend_schema(
        summary="شروع ارزیابی علائم",
        description="شروع فرآیند ارزیابی علائم بیمار",
        responses={200: dict}
    )
    @action(detail=False, methods=['post'])
    def start_symptom_assessment(self, request):
        """
        شروع ارزیابی علائم
        """
        try:
            chatbot_service = self.get_chatbot_service()
            assessment = chatbot_service.start_symptom_assessment()
            
            return Response(assessment)
            
        except Exception as e:
            return Response(
                {'error': f'خطا در شروع ارزیابی: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @extend_schema(
        summary="ارسال پاسخ‌های ارزیابی علائم",
        description="ارسال پاسخ‌های بیمار به سؤالات ارزیابی علائم",
        request=SymptomAssessmentRequestSerializer,
        responses={200: dict}
    )
    @action(detail=False, methods=['post'])
    def submit_symptom_assessment(self, request):
        """
        ارسال پاسخ‌های ارزیابی علائم
        """
        serializer = SymptomAssessmentRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            chatbot_service = self.get_chatbot_service()
            analysis = chatbot_service.process_symptom_response(serializer.validated_data)
            
            return Response(analysis)
            
        except Exception as e:
            return Response(
                {'error': f'خطا در تحلیل علائم: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @extend_schema(
        summary="درخواست نوبت",
        description="درخواست رزرو نوبت از طریق چت‌بات",
        request=AppointmentRequestSerializer,
        responses={200: dict}
    )
    @action(detail=False, methods=['post'])
    def request_appointment(self, request):
        """
        درخواست نوبت
        """
        serializer = AppointmentRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            chatbot_service = self.get_chatbot_service()
            appointment_info = chatbot_service.request_appointment(
                specialty=serializer.validated_data.get('specialty'),
                preferred_time=serializer.validated_data.get('preferred_time')
            )
            
            return Response(appointment_info)
            
        except Exception as e:
            return Response(
                {'error': f'خطا در درخواست نوبت: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @extend_schema(
        summary="پایان جلسه",
        description="پایان دادن به جلسه فعال چت‌بات",
        responses={200: dict}
    )
    @action(detail=False, methods=['post'])
    def end_session(self, request):
        """
        پایان جلسه
        """
        try:
            chatbot_service = self.get_chatbot_service()
            chatbot_service.end_session()
            
            return Response({'message': 'جلسه با موفقیت پایان یافت'})
            
        except Exception as e:
            return Response(
                {'error': f'خطا در پایان جلسه: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DoctorChatbotViewSet(viewsets.GenericViewSet):
    """
    API چت‌بات پزشکان
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_chatbot_service(self):
        """
        دریافت سرویس چت‌بات پزشک
        """
        return DoctorChatbotService(self.request.user)
    
    @extend_schema(
        summary="شروع جلسه چت‌بات پزشک",
        description="ایجاد یا دریافت جلسه فعال چت‌بات برای پزشک",
        responses={200: StartSessionResponseSerializer}
    )
    @action(detail=False, methods=['post'])
    def start_session(self, request):
        """
        شروع جلسه چت‌بات
        """
        try:
            chatbot_service = self.get_chatbot_service()
            session = chatbot_service.get_or_create_session()
            
            # دریافت پیام خوشامدگویی
            ai_response = chatbot_service.ai_service.response_matcher.get_greeting_response()
            greeting_message = None
            
            if ai_response:
                greeting_message = {
                    'content': ai_response.response_text,
                    'message_type': 'text',
                    'response_data': ai_response.response_data
                }
            
            # دریافت پاسخ‌های سریع اولیه
            quick_replies = chatbot_service.get_quick_replies()
            
            return Response({
                'session': ChatbotSessionSerializer(session).data,
                'greeting_message': greeting_message,
                'quick_replies': quick_replies
            })
            
        except Exception as e:
            return Response(
                {'error': f'خطا در شروع جلسه: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @extend_schema(
        summary="ارسال پیام به چت‌بات",
        description="ارسال پیام پزشک و دریافت پاسخ چت‌بات",
        request=SendMessageRequestSerializer,
        responses={200: SendMessageResponseSerializer}
    )
    @action(detail=False, methods=['post'])
    def send_message(self, request):
        """
        ارسال پیام به چت‌بات
        """
        serializer = SendMessageRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            chatbot_service = self.get_chatbot_service()
            
            # پردازش پیام
            result = chatbot_service.process_message(
                message=serializer.validated_data['message'],
                context=serializer.validated_data.get('context')
            )
            
            return Response(result)
            
        except Exception as e:
            return Response(
                {'error': f'خطا در پردازش پیام: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @extend_schema(
        summary="درخواست پشتیبانی تشخیصی",
        description="درخواست کمک در تشخیص بر اساس علائم بیمار",
        request=DiagnosisSupportRequestSerializer,
        responses={200: dict}
    )
    @action(detail=False, methods=['post'])
    def diagnosis_support(self, request):
        """
        درخواست پشتیبانی تشخیصی
        """
        serializer = DiagnosisSupportRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            chatbot_service = self.get_chatbot_service()
            
            patient_info = {
                'age': serializer.validated_data.get('patient_age'),
                'gender': serializer.validated_data.get('patient_gender'),
                'medical_history': serializer.validated_data.get('medical_history'),
                'current_medications': serializer.validated_data.get('current_medications', [])
            }
            
            diagnosis_support = chatbot_service.get_diagnosis_support(
                symptoms=serializer.validated_data['symptoms'],
                patient_info=patient_info
            )
            
            return Response(diagnosis_support)
            
        except Exception as e:
            return Response(
                {'error': f'خطا در پشتیبانی تشخیصی: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @extend_schema(
        summary="درخواست اطلاعات دارو",
        description="دریافت اطلاعات کامل در مورد دارو",
        request=MedicationInfoRequestSerializer,
        responses={200: dict}
    )
    @action(detail=False, methods=['post'])
    def medication_info(self, request):
        """
        درخواست اطلاعات دارو
        """
        serializer = MedicationInfoRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            chatbot_service = self.get_chatbot_service()
            
            patient_context = {
                'age': serializer.validated_data.get('patient_age'),
                'weight': serializer.validated_data.get('patient_weight'),
                'allergies': serializer.validated_data.get('allergies', []),
                'current_medications': serializer.validated_data.get('current_medications', [])
            }
            
            medication_info = chatbot_service.get_medication_info(
                medication_name=serializer.validated_data['medication_name'],
                patient_context=patient_context
            )
            
            return Response(medication_info)
            
        except Exception as e:
            return Response(
                {'error': f'خطا در دریافت اطلاعات دارو: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @extend_schema(
        summary="درخواست پروتکل درمان",
        description="دریافت پروتکل درمان برای بیماری مشخص",
        parameters=[
            OpenApiParameter('condition', OpenApiTypes.STR, description='نام بیماری'),
            OpenApiParameter('severity', OpenApiTypes.STR, description='شدت بیماری')
        ],
        responses={200: dict}
    )
    @action(detail=False, methods=['get'])
    def treatment_protocol(self, request):
        """
        درخواست پروتکل درمان
        """
        condition = request.query_params.get('condition')
        severity = request.query_params.get('severity', 'moderate')
        
        if not condition:
            return Response(
                {'error': 'نام بیماری الزامی است'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            chatbot_service = self.get_chatbot_service()
            protocol = chatbot_service.get_treatment_protocol(condition, severity)
            
            return Response(protocol)
            
        except Exception as e:
            return Response(
                {'error': f'خطا در دریافت پروتکل: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @extend_schema(
        summary="جستجو در مراجع پزشکی",
        description="جستجو در متون و مراجع پزشکی",
        parameters=[
            OpenApiParameter('query', OpenApiTypes.STR, description='عبارت جستجو'),
            OpenApiParameter('specialty', OpenApiTypes.STR, description='تخصص (اختیاری)')
        ],
        responses={200: dict}
    )
    @action(detail=False, methods=['get'])
    def search_references(self, request):
        """
        جستجو در مراجع پزشکی
        """
        query = request.query_params.get('query')
        specialty = request.query_params.get('specialty')
        
        if not query:
            return Response(
                {'error': 'عبارت جستجو الزامی است'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            chatbot_service = self.get_chatbot_service()
            search_results = chatbot_service.search_medical_references(query, specialty)
            
            return Response(search_results)
            
        except Exception as e:
            return Response(
                {'error': f'خطا در جستجو: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ChatbotSessionViewSet(BaseChatbotViewSet):
    """
    مدیریت جلسات چت‌بات
    """
    queryset = ChatbotSession.objects.all()
    serializer_class = ChatbotSessionSerializer
    
    def get_queryset(self):
        """
        فیلتر جلسات بر اساس کاربر فعلی
        """
        queryset = super().get_queryset()
        
        # فیلتر بر اساس نوع جلسه
        session_type = self.request.query_params.get('session_type')
        if session_type:
            queryset = queryset.filter(session_type=session_type)
        
        # فیلتر بر اساس وضعیت
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset.order_by('-started_at')


class ConversationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    مشاهده مکالمات چت‌بات
    """
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """
        فیلتر مکالمات بر اساس کاربر فعلی
        """
        return Conversation.objects.filter(
            session__user=self.request.user
        ).select_related('session').prefetch_related('messages').order_by('-started_at')
    
    def get_serializer_class(self):
        """
        انتخاب سریالایزر مناسب
        """
        if self.action == 'list':
            return ConversationListSerializer
        return ConversationSerializer
    
    @extend_schema(
        summary="دریافت تاریخچه مکالمه",
        description="دریافت تاریخچه کامل یک مکالمه با پیام‌ها",
        parameters=[
            OpenApiParameter('limit', OpenApiTypes.INT, description='تعداد پیام‌ها')
        ],
        responses={200: ConversationHistorySerializer}
    )
    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        """
        دریافت تاریخچه مکالمه
        """
        conversation = self.get_object()
        limit = int(request.query_params.get('limit', 50))
        
        messages = conversation.messages.order_by('-created_at')[:limit]
        total_messages = conversation.messages.count()
        
        return Response({
            'conversation': ConversationListSerializer(conversation).data,
            'messages': MessageSerializer(messages, many=True).data,
            'total_messages': total_messages,
            'has_more': total_messages > limit
        })


class MessageViewSet(viewsets.ReadOnlyModelViewSet):
    """
    مشاهده پیام‌های چت‌بات
    """
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """
        فیلتر پیام‌ها بر اساس کاربر فعلی
        """
        return Message.objects.filter(
            conversation__session__user=self.request.user
        ).select_related('conversation').order_by('-created_at')