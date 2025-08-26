"""
{APP_NAME} Serializers
Part of HELSSA Platform

This module defines DRF serializers for {APP_DESCRIPTION}
following the standard HELSSA serializer pattern.
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import {MainModel}

User = get_user_model()


class Base{MainModel}Serializer(serializers.ModelSerializer):
    """
    Base serializer for {MainModel} with common fields
    """
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    status_display = serializers.CharField(source='get_status_display_persian', read_only=True)
    
    class Meta:
        model = {MainModel}
        fields = [
            'id', 'title', 'description', 'status', 'status_display',
            'created_at', 'updated_at', 'created_by_name', 'is_active'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by_name']


class {MainModel}CreateSerializer(Base{MainModel}Serializer):
    """
    Serializer for creating new {MainModel} instances
    """
    class Meta(Base{MainModel}Serializer.Meta):
        fields = ['title', 'description']
    
    def validate_title(self, value):
        """Validate title field"""
        if len(value.strip()) < 3:
            raise serializers.ValidationError("عنوان باید حداقل 3 کاراکتر باشد")
        return value.strip()
    
    def create(self, validated_data):
        """Create new instance with current user"""
        validated_data['user'] = self.context['request'].user
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class {MainModel}DetailSerializer(Base{MainModel}Serializer):
    """
    Detailed serializer for {MainModel} with all fields
    """
    user_info = serializers.SerializerMethodField()
    
    class Meta(Base{MainModel}Serializer.Meta):
        fields = Base{MainModel}Serializer.Meta.fields + ['user_info']
    
    def get_user_info(self, obj):
        """Get user information"""
        if obj.user:
            return {
                'id': str(obj.user.id),
                'username': obj.user.username,
                'user_type': getattr(obj.user, 'user_type', 'unknown')
            }
        return None


class {MainModel}UpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating {MainModel} instances
    """
    class Meta:
        model = {MainModel}
        fields = ['title', 'description', 'status']
    
    def validate_status(self, value):
        """Validate status transitions"""
        if self.instance:
            current_status = self.instance.status
            
            # Define allowed transitions
            allowed_transitions = {
                'pending': ['processing', 'failed'],
                'processing': ['completed', 'failed'],
                'completed': [],  # No transitions from completed
                'failed': ['pending'],  # Can retry from failed
            }
            
            if value not in allowed_transitions.get(current_status, []):
                raise serializers.ValidationError(
                    f"تغییر وضعیت از '{current_status}' به '{value}' مجاز نیست"
                )
        
        return value


# Request/Response serializers for API endpoints
class {MainModel}RequestSerializer(serializers.Serializer):
    """
    Serializer for {APP_NAME} API requests
    """
    input_data = serializers.CharField(
        max_length=5000,
        help_text="ورودی درخواست"
    )
    options = serializers.JSONField(
        required=False,
        default=dict,
        help_text="تنظیمات اضافی"
    )
    
    def validate_input_data(self, value):
        """Validate input data"""
        if len(value.strip()) < 10:
            raise serializers.ValidationError("ورودی باید حداقل 10 کاراکتر باشد")
        return value.strip()


class {MainModel}ResponseSerializer(serializers.Serializer):
    """
    Serializer for {APP_NAME} API responses
    """
    success = serializers.BooleanField()
    message = serializers.CharField()
    data = serializers.JSONField(required=False)
    request_id = serializers.UUIDField(required=False)
    processing_time = serializers.FloatField(required=False)
    
    def to_representation(self, instance):
        """Custom representation for API responses"""
        data = super().to_representation(instance)
        
        # Add timestamp
        from django.utils import timezone
        data['timestamp'] = timezone.now().isoformat()
        
        return data