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
from django.contrib.auth import get_user_model
from .models import OTPDetails
from .serializers import OTPRequestSerializer
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
        
        
        








@swagger_auto_schema(
    method='post',
    operation_description="Generate and send OTP to the user's phone number",
    request_body=OTPRequestSerializer,
    responses={
        200: openapi.Response(
            description="OTP sent successfully",
            examples={
                "application/json": {
                    "error": False,
                    "detail": "OTP sent successfully"
                }
            }
        ),
        400: openapi.Response(
            description="Bad request",
            examples={
                "application/json": {
                    "phone_number": ["This field is required."]
                }
            }
        ),
        404: openapi.Response(
            description="User not found",
            examples={
                "application/json": {
                    "error": True,
                    "detail": "User not found"
                }
            }
        ),
        500: openapi.Response(
            description="Failed to send OTP",
            examples={
                "application/json": {
                    "error": True,
                    "detail": "Failed to send OTP"
                }
            }
        )
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def generate_and_send_otp(request):
    serializer = OTPRequestSerializer(data=request.data)
    if serializer.is_valid():
        phone_number = serializer.validated_data['phone_number']
        User = get_user_model()
        
        try:
            user = User.objects.get(phone_number=phone_number)
        except User.DoesNotExist:
            return Response({"error": True, "detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        
        # Generate a random 4-digit OTP
        otp_code = str(random.randint(1000, 9999))
        
        # Store or update the OTP in the database
        otp, created = OTPDetails.objects.update_or_create(
            phone_number=phone_number,
            defaults={'otp': otp_code},
        )
        
        # Send OTP using the provided code
        url = "https://www.fast2sms.com/dev/bulkV2"
        payload = f"variables_values={otp_code}&route=otp&numbers={phone_number}"
        headers = {
            'authorization': "lMeMGisGX2r8NsEwsckcpZABjcgTKUs3y91LubpGXAjebdBwlAUxJqk8NbAX",  # Replace with your actual API key
            'Content-Type': "application/x-www-form-urlencoded",
            'Cache-Control': "no-cache",
        }
        
        response = requests.request("POST", url, data=payload, headers=headers)
        
        response_data = response.json()
        
        if response_data.get("return"):
            return Response({"error": False, "detail": "OTP sent successfully"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": True, "detail": "Failed to send OTP"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        # return Response({"error": False, "detail": response.text}, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
















@swagger_auto_schema(
    method='post',
    operation_description="Verify OTP and return user details",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'phone_number': openapi.Schema(type=openapi.TYPE_STRING, description='Phone number of the user'),
            'otp': openapi.Schema(type=openapi.TYPE_STRING, description='OTP sent to the user')
        },
        required=['phone_number', 'otp']
    ),
    responses={
        200: openapi.Response(
            description="OTP verified successfully",
            examples={
                "application/json": {
                    "error": False,
                    "detail": "OTP verified successfully",
                    "token": "token_value",
                    "user_details": {
                        "id": 1,
                        "username": "user1",
                        "phone_number": "1234567890",
                        "name": "User One",
                        "email": "user1@example.com",
                        "slug": "userone",
                        "verified": True,
                        "wallet": {
                            "wallet_id": 1,
                            "balance": 100.0,
                            "last_modified": "2024-08-05T00:00:00Z"
                        },
                        "metric": {
                            "played": 0,
                            "win": 0,
                            "penalty": 0,
                            "referals": 0,
                            "referal_winnings": 0
                        }
                    }
                }
            }
        ),
        400: "Invalid OTP or missing data",
        404: "User or OTP not found",
        500: "Internal server error"
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def verify_otp(request):
    try:
        if request.method == "POST":
            phone_number = request.data.get('phone_number')
            otp_code = request.data.get('otp')

            # Validate request data
            if not phone_number or not otp_code:
                return Response(
                    {"error": True, "detail": "Phone number and OTP are required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Check if the OTP exists for the given phone number and matches the provided OTP
            try:
                otp_entry = OTPDetails.objects.get(phone_number=phone_number)
                if otp_entry.otp != otp_code:
                    return Response(
                        {"error": True, "detail": "Invalid OTP"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            except OTPDetails.DoesNotExist:
                return Response(
                    {"error": True, "detail": "OTP not found for the provided phone number"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Check if the user exists
            User = get_user_model()
            try:
                user = User.objects.get(phone_number=phone_number)
            except User.DoesNotExist:
                return Response(
                    {"error": True, "detail": "User not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Generate or get token
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
                    "withdrawable_balance": wallet.withdrawable_balance,
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
                "win": 0,
                "penalty": 0,
                "referals": 0,
                "referal_winnings": 0,
            }

            # Get additional user details
            user_details = {
                "id": user.id,
                "username": user.username,
                "phone_number": user.phone_number,
                "name": user.first_name + " " + user.last_name,
                "email": user.email,
                "slug": slug,
                "verified": user.verified,
                "kyc":user.kyc,
                "wallet": wallet_details,
                "metric": metric,
            }

            return Response(
                {
                    "error": False,
                    "detail": "OTP verified successfully",
                    "token": token.key,
                    "user_details": user_details,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {"error": True, "detail": "Invalid request method"},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )
    except Exception as e:
        return Response(
            {"error": True, "detail": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )