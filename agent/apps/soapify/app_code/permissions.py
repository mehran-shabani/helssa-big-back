from rest_framework import permissions


class IsDoctor(permissions.BasePermission):
    message = "Only doctors are allowed."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and getattr(request.user, "is_doctor", False))


class IsPatient(permissions.BasePermission):
    message = "Only patients are allowed."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and getattr(request.user, "is_patient", False))