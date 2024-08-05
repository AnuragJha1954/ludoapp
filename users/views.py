from django.shortcuts import render

from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .serializers import CustomUserCreateSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import logging

# Set up logging
logger = logging.getLogger(__name__)
# Create your views here.



@swagger_auto_schema(
    method='post',
    operation_description="Create a new user",
    request_body=CustomUserCreateSerializer,
    responses={
        201: openapi.Response(
            description="User created successfully",
            examples={
                "application/json": {
                    "error": False,
                    "detail": "User created successfully",
                    "user": {
                        "id": 1,
                        "username": "john_doe",
                        "email": "john@example.com",
                        "phone_number": "1234567890",
                        "verified": False
                    }
                }
            }
        ),
        400: openapi.Response(
            description="Bad request",
            examples={
                "application/json": {
                    "error": True,
                    "detail": {
                        "username": ["This field is required."]
                    }
                }
            }
        )
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def create_user(request):
    serializer = CustomUserCreateSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response({
            "error": False,
            "detail": "User created successfully",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "phone_number": user.phone_number,
                "verified": user.verified
            }
        }, status=status.HTTP_201_CREATED)
    return Response({"error": True, "detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
