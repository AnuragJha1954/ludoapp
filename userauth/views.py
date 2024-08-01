from django.shortcuts import render

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .serializers import CustomUserLoginSerializer
from users.models import CustomUser
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import random
import requests
from django.http import JsonResponse
from .models import OTPDetails
from .serializers import OTPRequestSerializer
from api.models import Wallet
import logging

# Set up logging
logger = logging.getLogger(__name__)

@swagger_auto_schema(
    method="post",
    request_body=CustomUserLoginSerializer,
    responses={
        status.HTTP_200_OK: "User Logged in successfully",
        status.HTTP_400_BAD_REQUEST: "Invalid credentials",
    },
)
@api_view(["POST"])
@permission_classes([AllowAny])
def user_login(request):
    try:
        if request.method == "POST":
            serializer = CustomUserLoginSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.validated_data["user"]
                token, _ = Token.objects.get_or_create(user=user)

                # Generate slug from first name and last name
                slug = (user.first_name + user.last_name).lower().replace(" ", "")

                # Get wallet details
                try:
                    wallet = Wallet.objects.get(user=user)
                    wallet_details = {
                        "wallet_id": wallet.id,
                        "balance": wallet.balance,
                        "last_modified": wallet.last_modified,
                    }
                except Wallet.DoesNotExist:
                    wallet_details = {
                        "wallet_id": None,
                        "balance": 0,
                        "last_modified": None,
                    }

                # Metric details
                metric = {
                    "played": 0,
                    "win":0,
                    "penalty":0,
                    "referals":0,
                    "referal_winnings":0,
                }
                
                # Get additional user details
                user_details = {
                    "id": user.id,
                    "username": user.username,
                    "phone_number": user.phone_number,
                    "name": user.first_name + " " + user.last_name,
                    "email": user.email,
                    "slug": slug,
                    "verified":user.verified,
                    "wallet": wallet_details,
                    "metric": metric,
                }
                
                return Response(
                    {
                        "error": False,
                        "detail": "User logged in successfully",
                        "token": token.key,
                        "user_details": user_details,
                    },
                    status=status.HTTP_200_OK,
                )

            return Response(
                {"error": True, "detail": "Invalid username or password "},
                status=status.HTTP_400_BAD_REQUEST,
            )
    except Exception as e:
        return Response(
            {"error": True, "detail": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
        
        






@swagger_auto_schema(
    method="post",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'old_password': openapi.Schema(type=openapi.TYPE_STRING, description='Old password'),
            'new_password': openapi.Schema(type=openapi.TYPE_STRING, description='New password'),
        },
        required=['old_password', 'new_password']
    ),
    responses={
        status.HTTP_200_OK: openapi.Response(description="Password reset successful"),
        status.HTTP_400_BAD_REQUEST: openapi.Response(description="Password reset unsuccessful"),
    },
)
@api_view(["POST"])
@permission_classes([AllowAny])
def forgot_password(request, user_id):
    if request.method == "POST":
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")

        print(old_password)
        
        if not old_password or not new_password:
            return Response(
                {"error": True, "detail": "Both old and new passwords are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return Response(
                {"error": True, "detail": "Invalid User"},
                status=status.HTTP_400_BAD_REQUEST,
            )
            

        if not user.check_password(old_password):
            return Response(
                {"error": True, "detail": "Old password does not match"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(new_password)
        user.save()

        return Response(
            {"error": False, "detail": "Password reset successfully"},
            status=status.HTTP_200_OK,
        )
        
        
        



def generate_random_otp():
    return str(random.randint(100000, 999999))



def send_sms(data):
    url = 'https://control.msg91.com/api/v5/otp?template_id=&mobile=&authkey=&realTimeResponse='
    headers = {
        'Content-Type': 'application/JSON',
    }
    response = requests.post(url, headers=headers, json=data)
    return response




@swagger_auto_schema(
    method='post',
    request_body=OTPRequestSerializer,
    responses={
        200: openapi.Response(
            description="OTP sent successfully.",
            examples={
                'application/json': {
                    "message": "OTP sent successfully."
                }
            }
        ),
        400: openapi.Response(
            description="Invalid input.",
            examples={
                'application/json': {
                    "phone_number": ["This field is required."]
                }
            }
        ),
        500: openapi.Response(
            description="Failed to send OTP.",
            examples={
                'application/json': {
                    "error": "Failed to send OTP."
                }
            }
        )
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def generate_otp(request):
    serializer = OTPRequestSerializer(data=request.data)
    if serializer.is_valid():
        phone_number = serializer.validated_data['phone_number']
        otp = generate_random_otp()

        # Store OTP details
        otp_details, created = OTPDetails.objects.update_or_create(
            phone_number=phone_number,
            defaults={'otp': otp}
        )

        # Prepare data for SMS API
        sms_data = {
            "Param1": otp,  # OTP value
            "Param2": phone_number,  # Phone number
            "Param3": f"Your OTP is {otp}"  # Message body
        }

        sms_response = send_sms(sms_data)

        if sms_response.status_code == 200:
            return JsonResponse({"message": "OTP sent successfully."}, status=200)
        else:
            return JsonResponse({"error": "Failed to send OTP."}, status=500)
    return JsonResponse(serializer.errors, status=400)











@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'phone_number': openapi.Schema(type=openapi.TYPE_STRING),
            'otp': openapi.Schema(type=openapi.TYPE_STRING),
        },
        required=['phone_number', 'otp']
    ),
    responses={
        200: openapi.Response(
            description="OTP verified successfully.",
            examples={
                'application/json': {
                    "message": "OTP verified successfully."
                }
            }
        ),
        400: openapi.Response(
            description="Invalid OTP or phone number.",
            examples={
                'application/json': {
                    "error": "OTP does not match."
                }
            }
        )
    }
)
@api_view(['POST'])
def verify_otp(request):
    phone_number = request.data.get('phone_number')
    otp = request.data.get('otp')

    if not phone_number or not otp:
        return Response({"error": "Phone number and OTP are required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        otp_details = OTPDetails.objects.get(phone_number=phone_number)
    except OTPDetails.DoesNotExist:
        return Response({"error": "Phone number not found."}, status=status.HTTP_400_BAD_REQUEST)

    if otp_details.otp == otp:
        try:
            user = CustomUser.objects.get(phone_number=phone_number)
            user.verified = True
            user.save()
            return Response({"message": "OTP verified successfully."}, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({"error": "User not found for the given phone number."}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({"error": "OTP does not match."}, status=status.HTTP_400_BAD_REQUEST)