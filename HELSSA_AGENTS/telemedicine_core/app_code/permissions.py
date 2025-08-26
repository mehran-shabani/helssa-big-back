"""
{APP_NAME} Permissions
Part of HELSSA Platform

Custom permissions for {APP_DESCRIPTION}
"""

from rest_framework import permissions
from django.contrib.auth import get_user_model

User = get_user_model()


class IsPatientOrDoctor(permissions.BasePermission):
    """
    Permission that allows access to patients and doctors only
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        return hasattr(request.user, 'user_type') and request.user.user_type in ['patient', 'doctor']


class IsOwnerOrDoctor(permissions.BasePermission):
    """
    Permission that allows:
    - Patients to access only their own records
    - Doctors to access any record (with proper authorization)
    """
    
    def has_object_permission(self, request, view, obj):
        # Owner can always access their own records
        if hasattr(obj, 'user') and obj.user == request.user:
            return True
        
        # Doctors can access records with proper authorization
        if hasattr(request.user, 'user_type') and request.user.user_type == 'doctor':
            # TODO: Implement proper doctor authorization logic
            # This should check if doctor has been granted access to this patient
            return True
        
        return False


class {MainModel}Permission(permissions.BasePermission):
    """
    Custom permission for {MainModel} operations
    """
    
    def has_permission(self, request, view):
        """Check general permission for the view"""
        
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Check user type
        if not hasattr(request.user, 'user_type'):
            return False
        
        user_type = request.user.user_type
        
        # Define permissions based on action
        if view.action in ['create', 'update', 'partial_update']:
            # Both patients and doctors can create/update
            return user_type in ['patient', 'doctor']
        
        elif view.action in ['list', 'retrieve']:
            # Both can read with proper filtering
            return user_type in ['patient', 'doctor']
        
        elif view.action == 'destroy':
            # Only owners can delete (or doctors with proper auth)
            return user_type in ['patient', 'doctor']
        
        # Default: allow if authenticated
        return True
    
    def has_object_permission(self, request, view, obj):
        """Check permission for specific object"""
        
        # Owner always has access
        if hasattr(obj, 'user') and obj.user == request.user:
            return True
        
        # Doctors need special authorization
        if request.user.user_type == 'doctor':
            return self._check_doctor_authorization(request.user, obj)
        
        return False
    
    def _check_doctor_authorization(self, doctor, obj):
        """
        Check if doctor is authorized to access this object
        This should integrate with unified_access service
        """
        # TODO: Implement proper authorization check
        # For now, return True - but this should be implemented properly
        return True


class ReadOnlyForPatients(permissions.BasePermission):
    """
    Permission that allows:
    - Doctors: full access (CRUD)
    - Patients: read-only access to their own records
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        user_type = getattr(request.user, 'user_type', None)
        
        if user_type == 'doctor':
            return True
        elif user_type == 'patient':
            # Patients can only read
            return request.method in permissions.SAFE_METHODS
        
        return False
    
    def has_object_permission(self, request, view, obj):
        # Doctors have full access
        if request.user.user_type == 'doctor':
            return True
        
        # Patients can only read their own records
        if request.user.user_type == 'patient':
            return (
                request.method in permissions.SAFE_METHODS and 
                hasattr(obj, 'user') and 
                obj.user == request.user
            )
        
        return False


class DoctorOnlyPermission(permissions.BasePermission):
    """
    Permission that allows access to doctors only
    """
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and
            getattr(request.user, 'user_type', None) == 'doctor'
        )