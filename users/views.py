from django.shortcuts import render

from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserCreationSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import logging

# Set up logging
logger = logging.getLogger(__name__)
# Create your views here.



@swagger_auto_schema(
    method='post',
    request_body=UserCreationSerializer,
    responses={
        201: openapi.Response(
            description="User created successfully.",
            examples={
                'application/json': {
                    "message": "User created successfully."
                }
            }
        ),
        400: openapi.Response(
            description="Invalid input data.",
            examples={
                'application/json': {
                    "username": ["This field is required."],
                    "password": ["This field is required."],
                    "email": ["This field is required."],
                    # You can add more specific error examples based on the serializer validation
                }
            }
        )
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def create_user(request):
    serializer = UserCreationSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "User created successfully."}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
