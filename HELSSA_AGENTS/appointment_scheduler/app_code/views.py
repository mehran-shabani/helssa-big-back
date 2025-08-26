"""
{APP_NAME} Views
Part of HELSSA Platform

This module defines API views for {APP_DESCRIPTION}
following the standard HELSSA view pattern with delegation to cores.
"""

import logging
import time
from typing import Dict, Any
from django.http import HttpRequest
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser

# Unified imports
from unified_auth.decorators import unified_auth_required
from unified_auth.permissions import IsPatient, IsDoctor

# App imports
from .cores.orchestrator import CentralOrchestrator
from .serializers import (
    {MainModel}RequestSerializer,
    {MainModel}ResponseSerializer,
    {MainModel}DetailSerializer,
    {MainModel}CreateSerializer
)
from .models import {MainModel}

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@unified_auth_required(user_types=['patient', 'doctor'])
def primary_endpoint(request: HttpRequest) -> Response:
    """
    Primary API endpoint for {APP_NAME}
    
    Handles the main functionality of {APP_DESCRIPTION}
    """
    start_time = time.time()
    orchestrator = CentralOrchestrator()
    
    try:
        logger.info(f"Primary endpoint called by user {request.user.username}")
        
        # 1. Validate input
        serializer = {MainModel}RequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {
                    'success': False,
                    'error': 'ورودی نامعتبر',
                    'details': serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 2. Execute workflow through orchestrator
        result = orchestrator.execute_primary_workflow(
            request_data=serializer.validated_data,
            user=request.user,
            workflow_type='{PRIMARY_WORKFLOW}'
        )
        
        # 3. Log request
        orchestrator.api_ingress.log_request(
            request=request,
            action='{PRIMARY_WORKFLOW}',
            processing_time=time.time() - start_time
        )
        
        # 4. Return success response
        return orchestrator.api_ingress.create_success_response(
            data=result,
            message='درخواست با موفقیت پردازش شد'
        )
        
    except PermissionError as e:
        logger.warning(f"Permission denied for user {request.user.username}: {str(e)}")
        return orchestrator.api_ingress.create_error_response(
            error_message="دسترسی مجاز نیست",
            status_code=status.HTTP_403_FORBIDDEN
        )
        
    except Exception as e:
        logger.error(f"Primary endpoint error: {str(e)}")
        return orchestrator.api_ingress.create_error_response(
            error_message="خطای داخلی سرور",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@unified_auth_required(user_types=['patient', 'doctor'])
def text_processing_endpoint(request: HttpRequest) -> Response:
    """
    Text processing endpoint for {APP_NAME}
    
    Handles text analysis, generation, and medical text processing
    """
    start_time = time.time()
    orchestrator = CentralOrchestrator()
    
    try:
        logger.info(f"Text processing endpoint called by user {request.user.username}")
        
        # Validate input
        required_fields = ['text', 'processing_type']
        for field in required_fields:
            if field not in request.data:
                return orchestrator.api_ingress.create_error_response(
                    error_message=f"فیلد {field} الزامی است"
                )
        
        # Execute text processing workflow
        result = orchestrator.execute_primary_workflow(
            request_data=request.data,
            user=request.user,
            workflow_type='{TEXT_PROCESSING_WORKFLOW}'
        )
        
        # Log request
        orchestrator.api_ingress.log_request(
            request=request,
            action='{TEXT_PROCESSING_WORKFLOW}',
            processing_time=time.time() - start_time
        )
        
        return orchestrator.api_ingress.create_success_response(
            data=result,
            message='پردازش متن با موفقیت انجام شد'
        )
        
    except Exception as e:
        logger.error(f"Text processing endpoint error: {str(e)}")
        return orchestrator.api_ingress.create_error_response(
            error_message="خطا در پردازش متن",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
@unified_auth_required(user_types=['patient', 'doctor'])
def audio_processing_endpoint(request: HttpRequest) -> Response:
    """
    Audio processing endpoint for {APP_NAME}
    
    Handles audio file upload and speech-to-text conversion
    """
    start_time = time.time()
    orchestrator = CentralOrchestrator()
    
    try:
        logger.info(f"Audio processing endpoint called by user {request.user.username}")
        
        # Check for audio file
        if 'audio_file' not in request.FILES:
            return orchestrator.api_ingress.create_error_response(
                error_message="فایل صوتی ارسال نشده است"
            )
        
        audio_file = request.FILES['audio_file']
        processing_type = request.data.get('processing_type', 'transcription')
        
        # Prepare request data
        request_data = {
            'audio_file': audio_file,
            'processing_type': processing_type,
            'language': request.data.get('language', 'fa')
        }
        
        # Execute audio processing workflow
        result = orchestrator.execute_primary_workflow(
            request_data=request_data,
            user=request.user,
            workflow_type='{AUDIO_PROCESSING_WORKFLOW}'
        )
        
        # Log request
        orchestrator.api_ingress.log_request(
            request=request,
            action='{AUDIO_PROCESSING_WORKFLOW}',
            processing_time=time.time() - start_time
        )
        
        return orchestrator.api_ingress.create_success_response(
            data=result,
            message='پردازش فایل صوتی با موفقیت انجام شد'
        )
        
    except Exception as e:
        logger.error(f"Audio processing endpoint error: {str(e)}")
        return orchestrator.api_ingress.create_error_response(
            error_message="خطا در پردازش فایل صوتی",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@unified_auth_required(user_types=['patient', 'doctor'])
def get_history(request: HttpRequest) -> Response:
    """
    Get user's workflow history
    """
    orchestrator = CentralOrchestrator()
    
    try:
        limit = int(request.GET.get('limit', 10))
        limit = min(limit, 50)  # Maximum 50 records
        
        history = orchestrator.get_user_workflow_history(
            user=request.user,
            limit=limit
        )
        
        return orchestrator.api_ingress.create_success_response(
            data={'history': history},
            message='تاریخچه با موفقیت دریافت شد'
        )
        
    except Exception as e:
        logger.error(f"Get history error: {str(e)}")
        return orchestrator.api_ingress.create_error_response(
            error_message="خطا در دریافت تاریخچه"
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@unified_auth_required(user_types=['patient', 'doctor'])
def get_record_detail(request: HttpRequest, record_id: str) -> Response:
    """
    Get detailed information for a specific record
    """
    orchestrator = CentralOrchestrator()
    
    try:
        # Get record
        record = {MainModel}.objects.get(
            id=record_id,
            user=request.user
        )
        
        # Serialize record
        serializer = {MainModel}DetailSerializer(record)
        
        return orchestrator.api_ingress.create_success_response(
            data=serializer.data,
            message='جزئیات رکورد با موفقیت دریافت شد'
        )
        
    except {MainModel}.DoesNotExist:
        return orchestrator.api_ingress.create_error_response(
            error_message="رکورد یافت نشد",
            status_code=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Get record detail error: {str(e)}")
        return orchestrator.api_ingress.create_error_response(
            error_message="خطا در دریافت جزئیات رکورد"
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@unified_auth_required(user_types=['patient', 'doctor'])
def create_record(request: HttpRequest) -> Response:
    """
    Create a new record manually
    """
    orchestrator = CentralOrchestrator()
    
    try:
        # Validate input
        serializer = {MainModel}CreateSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if not serializer.is_valid():
            return orchestrator.api_ingress.create_error_response(
                error_message="داده‌های ورودی نامعتبر"
            )
        
        # Create record
        record = serializer.save()
        
        # Serialize response
        response_serializer = {MainModel}DetailSerializer(record)
        
        return orchestrator.api_ingress.create_success_response(
            data=response_serializer.data,
            message='رکورد با موفقیت ایجاد شد'
        )
        
    except Exception as e:
        logger.error(f"Create record error: {str(e)}")
        return orchestrator.api_ingress.create_error_response(
            error_message="خطا در ایجاد رکورد"
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@unified_auth_required(user_types=['patient', 'doctor'])
def get_workflow_status(request: HttpRequest, workflow_id: str) -> Response:
    """
    Get status of a specific workflow
    """
    orchestrator = CentralOrchestrator()
    
    try:
        # Try to get cached result
        result = orchestrator.get_cached_result(workflow_id)
        
        if result:
            return orchestrator.api_ingress.create_success_response(
                data=result,
                message='وضعیت گردش کار دریافت شد'
            )
        else:
            return orchestrator.api_ingress.create_error_response(
                error_message="گردش کار یافت نشد یا منقضی شده است",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
    except Exception as e:
        logger.error(f"Get workflow status error: {str(e)}")
        return orchestrator.api_ingress.create_error_response(
            error_message="خطا در دریافت وضعیت گردش کار"
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@unified_auth_required(user_types=['doctor'])  # Doctor only
def get_analytics(request: HttpRequest) -> Response:
    """
    Get analytics data (Doctor only)
    """
    orchestrator = CentralOrchestrator()
    
    try:
        # Simple analytics - can be expanded
        total_records = {MainModel}.objects.filter(created_by=request.user).count()
        recent_records = {MainModel}.objects.filter(
            created_by=request.user,
            created_at__gte=timezone.now() - timedelta(days=30)
        ).count()
        
        analytics_data = {
            'total_records': total_records,
            'recent_records': recent_records,
            'user_type': request.user.user_type,
            'app_name': '{APP_NAME}'
        }
        
        return orchestrator.api_ingress.create_success_response(
            data=analytics_data,
            message='آمار با موفقیت دریافت شد'
        )
        
    except Exception as e:
        logger.error(f"Get analytics error: {str(e)}")
        return orchestrator.api_ingress.create_error_response(
            error_message="خطا در دریافت آمار"
        )


# Health check endpoint
@api_view(['GET'])
def health_check(request: HttpRequest) -> Response:
    """
    Health check endpoint for monitoring
    """
    return Response(
        {
            'status': 'healthy',
            'app': '{APP_NAME}',
            'timestamp': time.time()
        },
        status=status.HTTP_200_OK
    )