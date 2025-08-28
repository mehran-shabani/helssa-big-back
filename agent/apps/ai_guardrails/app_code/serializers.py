"""
سریالایزرهای اپلیکیشن
Application Serializers
"""

from rest_framework import serializers
from app_standards.serializers.base_serializers import BaseModelSerializer
from .models import GuardrailPolicy, RedFlagRule, PolicyViolationLog
from django.conf import settings
from typing import List, Dict, Any

class GuardrailPolicySerializer(BaseModelSerializer):
    """
    سریالایزر سیاست گاردریل
    """

    class Meta:
        model = GuardrailPolicy
        fields = [
            'id', 'name', 'description', 'is_active', 'enforcement_mode',
            'applies_to', 'priority', 'conditions', 'created_at', 'updated_at', 'created_by'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by']


class RedFlagRuleSerializer(BaseModelSerializer):
    """
    سریالایزر قانون رد-فلگ
    """

    class Meta:
        model = RedFlagRule
        fields = [
            'id', 'name', 'pattern_type', 'pattern', 'category', 'severity',
            'is_active', 'metadata', 'created_at', 'updated_at', 'created_by'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by']


class PolicyViolationLogSerializer(BaseModelSerializer):
    """
    سریالایزر گزارش نقض سیاست
    """

    class Meta:
        model = PolicyViolationLog
        fields = [
            'id', 'user', 'policy', 'rule', 'content_snapshot', 'direction',
            'context', 'action_taken', 'risk_score', 'matched_spans',
            'request_path', 'ip_address', 'user_agent', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class EvaluateContentSerializer(serializers.Serializer):
    """
    ورودی ارزیابی محتوای AI
    """
    content = serializers.CharField(
        min_length=1,
        max_length=getattr(settings, 'AI_GUARDRAILS', {}).get('MAX_CONTENT_LENGTH', 5000)
    )
    direction = serializers.ChoiceField(choices=['input', 'output', 'both'], default='both')
    context = serializers.DictField(required=False)


class EvaluationResultSerializer(serializers.Serializer):
    """
    خروجی ارزیابی محتوای AI
    """
    allowed = serializers.BooleanField()
    action = serializers.ChoiceField(choices=['allow', 'warn', 'block'])
    risk_score = serializers.IntegerField()
    reasons = serializers.ListField(child=serializers.CharField(), default=list)
    matches = serializers.ListField(child=serializers.DictField(), default=list)
    applied_policy = serializers.CharField(allow_blank=True, required=False)
