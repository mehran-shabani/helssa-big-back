from rest_framework import status, permissions, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .models import ExampleEntity
from .serializers import ExampleEntitySerializer


@api_view(["GET"])  # Health check endpoint
@permission_classes([permissions.AllowAny])
def health(request):
    return Response({"status": "ok", "app": "doctor_dashboard"}, status=status.HTTP_200_OK)


class ExampleEntityListCreateView(generics.ListCreateAPIView):
    queryset = ExampleEntity.objects.all().order_by("-created_at")
    serializer_class = ExampleEntitySerializer
    permission_classes = [permissions.IsAuthenticated]


class ExampleEntityRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ExampleEntity.objects.all()
    serializer_class = ExampleEntitySerializer
    permission_classes = [permissions.IsAuthenticated]