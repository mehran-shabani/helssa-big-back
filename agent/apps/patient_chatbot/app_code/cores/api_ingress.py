from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response


@api_view(["POST"])  # Standardized API ingress
@permission_classes([permissions.IsAuthenticated])
def handle_request(request):
    try:
        payload = request.data
        # TODO: validate payload via serializer (scaffold will inject)
        # TODO: delegate to orchestrator/text/speech cores as per app PLAN
        return Response({"success": True, "data": {}}, status=status.HTTP_200_OK)
    except Exception as exc:
        return Response({"success": False, "message": str(exc)}, status=status.HTTP_400_BAD_REQUEST)