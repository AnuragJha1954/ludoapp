from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Room, Wallet, WithdrawalHistory, DepositHistory, RoomResults,Challenge
from .serializers import RoomCreationSerializer, WalletCreationSerializer, DepositHistorySerializer, WithdrawalHistorySerializer, RoomResultsSerializer, ChallengeSerializer, UserSerializer
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from decimal import Decimal, InvalidOperation
import random
import logging

# Set up logging
logger = logging.getLogger(__name__)


# Create your views here.

@swagger_auto_schema(
    method='post',
    manual_parameters=[
        openapi.Parameter(
            'user_id',
            in_=openapi.IN_PATH,
            description="The ID of the user creating the room.",
            type=openapi.TYPE_INTEGER,
            required=True
        ),
    ],
    request_body=RoomCreationSerializer,
    responses={
        201: openapi.Response(
            description="Room created successfully.",
            examples={
                'application/json': {
                    "room_id": 1,
                    "user_id": 1,
                    "room_amount": "100.00"
                }
            }
        ),
        400: openapi.Response(
            description="Invalid input data.",
            examples={
                'application/json': {
                    "room_id": ["This field is required."],
                    "room_amount": ["This field is required."]
                }
            }
        ),
        403: openapi.Response(
            description="Forbidden access.",
            examples={
                'application/json': {
                    "error": "User not authenticated or ID mismatch."
                }
            }
        )
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def create_room(request, user_id):
    try:
        user = request.user  # Assumes the user is authenticated and available in request
        if not user or user.id != user_id:
            return Response({"error": "User not authenticated or ID mismatch."}, status=status.HTTP_403_FORBIDDEN)

        # Create a serializer instance with the request data and user context
        serializer = RoomCreationSerializer(data=request.data, context={'user': user})
        
        if serializer.is_valid():
            validated_data = serializer.validated_data

            # Retrieve the wallet for the user
            try:
                wallet = Wallet.objects.get(user=user)
            except Wallet.DoesNotExist:
                return Response({"error": "Wallet not found"}, status=status.HTTP_404_NOT_FOUND)

            # Check if the user has enough balance
            if wallet.balance < validated_data['room_amount']:
                return Response({"error": "Insufficient balance"}, status=status.HTTP_400_BAD_REQUEST)

            # Deduct the room amount from the wallet balance
            wallet.balance -= validated_data['room_amount']
            wallet.save()

            # Create the room
            room = Room.objects.create(user=user, **validated_data)

            # Generate a random challenge ID with format BLxxxxx
            challenge_id = f"BL{random.randint(10000, 99999)}"

            # Create the challenge
            Challenge.objects.create(
                challenge_id=challenge_id,
                room=room,
                created_by=user,
                status='O'  # Initial status is 'Open'
            )

            # Return the details of the created room
            return Response({
                "room_id": room.room_id,
                "user_id": room.user.id,
                "room_amount": room.room_amount,
                "challenge_id": challenge_id,
                "status": 'O'  # Return the initial status
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)








@swagger_auto_schema(
    method='post',
    manual_parameters=[
        openapi.Parameter(
            'user_id',
            in_=openapi.IN_PATH,
            description="The ID of the user for whom the wallet is being created.",
            type=openapi.TYPE_INTEGER,
            required=True
        ),
    ],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'balance': openapi.Schema(type=openapi.TYPE_NUMBER, format=openapi.FORMAT_DECIMAL)
        },
        required=['balance']
    ),
    responses={
        201: openapi.Response(
            description="Wallet created successfully.",
            examples={
                'application/json': {
                    "user_id": 1,
                    "balance": "0.00"
                }
            }
        ),
        400: openapi.Response(
            description="Invalid input data.",
            examples={
                'application/json': {
                    "balance": ["This field is required."]
                }
            }
        ),
        403: openapi.Response(
            description="Forbidden access.",
            examples={
                'application/json': {
                    "error": "User not authenticated or ID mismatch."
                }
            }
        )
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def create_wallet(request, user_id):
    try:
        user = request.user  # Assumes the user is authenticated and available in request
        if not user or user.id != user_id:
            return Response({"error": "User not authenticated or ID mismatch."}, status=status.HTTP_403_FORBIDDEN)
        
        # Set balance to 0 by default
        data = {'balance': 0}
        serializer = WalletCreationSerializer(data=data, context={'user': user})
        
        if serializer.is_valid():
            wallet = serializer.save()
            return Response({
                "user_id": wallet.user.id,
                "balance": str(wallet.balance)
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    
    





@swagger_auto_schema(
    method='post',
    manual_parameters=[
        openapi.Parameter(
            'wallet_id',
            in_=openapi.IN_PATH,
            description="The ID of the wallet where the deposit is being made.",
            type=openapi.TYPE_INTEGER,
            required=True
        ),
    ],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'deposit_amount': openapi.Schema(type=openapi.TYPE_NUMBER, format=openapi.FORMAT_DECIMAL),
            'proof_screenshot': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_URI)
        },
        required=['deposit_amount']
    ),
    responses={
        201: openapi.Response(
            description="Deposit entry created successfully.",
            examples={
                'application/json': {
                    "wallet_id": 1,
                    "deposit_amount": "100.00",
                    "deposit_date": "2024-07-26T00:00:00Z",
                    "status": "P",
                    "proof_screenshot": "http://example.com/proof.png"
                }
            }
        ),
        400: openapi.Response(
            description="Invalid input data.",
            examples={
                'application/json': {
                    "deposit_amount": ["This field is required."],
                    "proof_screenshot": ["Invalid file type."]
                }
            }
        ),
        404: openapi.Response(
            description="Wallet not found.",
            examples={
                'application/json': {
                    "error": "Wallet with the given ID not found."
                }
            }
        )
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def create_deposit(request, wallet_id):
    try:
        wallet = Wallet.objects.get(id=wallet_id)
    except Wallet.DoesNotExist:
        return Response({"error": "Wallet with the given ID not found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = DepositHistorySerializer(data=request.data, context={'wallet': wallet})
    
    if serializer.is_valid():
        deposit = serializer.save()
        
         # Build the absolute URL for the proof_screenshot
        if deposit.proof_screenshot:
            proof_screenshot_url = request.build_absolute_uri(deposit.proof_screenshot.url)
        else:
            proof_screenshot_url = None
        
        return Response({
            "error":False,
            "detail":"Deposit request submitted successfully",
            "wallet_id": deposit.wallet.id,
            "deposit_amount": str(deposit.deposit_amount),
            "deposit_date": deposit.deposit_date.isoformat(),
            "status": deposit.status,
            "proof_screenshot": proof_screenshot_url
        }, status=status.HTTP_201_CREATED)
    return Response({"error":True,"detail":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)








@swagger_auto_schema(
    method='post',
    manual_parameters=[
        openapi.Parameter(
            'wallet_id',
            in_=openapi.IN_PATH,
            description="The ID of the wallet from which the withdrawal is made.",
            type=openapi.TYPE_INTEGER,
            required=True
        ),
    ],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'withdrawal_amount': openapi.Schema(type=openapi.TYPE_NUMBER, format=openapi.FORMAT_DECIMAL)
        },
        required=['withdrawal_amount']
    ),
    responses={
        201: openapi.Response(
            description="Withdrawal entry created successfully.",
            examples={
                'application/json': {
                    "wallet_id": 1,
                    "withdrawal_amount": "50.00",
                    "withdrawal_date": "2024-07-26T00:00:00Z",
                    "status": "P"
                }
            }
        ),
        400: openapi.Response(
            description="Invalid input data.",
            examples={
                'application/json': {
                    "withdrawal_amount": ["This field is required."]
                }
            }
        ),
        404: openapi.Response(
            description="Wallet not found.",
            examples={
                'application/json': {
                    "error": "Wallet with the given ID not found."
                }
            }
        )
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def create_withdrawal(request, wallet_id):
    try:
        wallet = Wallet.objects.get(id=wallet_id)
    except Wallet.DoesNotExist:
        return Response({"error": True, "detail": "Wallet with the given ID not found."}, status=status.HTTP_404_NOT_FOUND)

    # Check if the wallet has sufficient balance
    withdrawal_amount_str = request.data.get('withdrawal_amount')
    if withdrawal_amount_str:
        try:
            withdrawal_amount = Decimal(withdrawal_amount_str)
        except (ValueError, InvalidOperation):
            return Response({"error": True, "detail": "Invalid withdrawal amount."}, status=status.HTTP_400_BAD_REQUEST)
        
        if wallet.balance < withdrawal_amount:
            return Response({"error": True, "detail": "Insufficient balance."}, status=status.HTTP_400_BAD_REQUEST)

    serializer = WithdrawalHistorySerializer(data=request.data, context={'wallet': wallet})
    
    if serializer.is_valid():
        withdrawal = serializer.save()

        # Deduct the withdrawal amount from the wallet balance
        wallet.balance -= withdrawal_amount
        wallet.save()

        return Response({
            "wallet_id": withdrawal.wallet.id,
            "withdrawal_amount": str(withdrawal.withdrawal_amount),
            "withdrawal_date": withdrawal.withdrawal_date.isoformat(),
            "status": withdrawal.status,
            "selected_tab": withdrawal.selected_tab,
            "account_holder_name": withdrawal.account_holder_name,
            "account_number": withdrawal.account_number,
            "ifsc_code": withdrawal.ifsc_code,
            "upi_id": withdrawal.upi_id,
        }, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)










@swagger_auto_schema(
    method='post',
    manual_parameters=[
        openapi.Parameter(
            'user_id',
            in_=openapi.IN_PATH,
            description="The ID of the user who is associated with the room result.",
            type=openapi.TYPE_INTEGER,
            required=True
        ),
        openapi.Parameter(
            'room_id',
            in_=openapi.IN_PATH,
            description="The ID of the room for which the result is being recorded.",
            type=openapi.TYPE_INTEGER,
            required=True
        ),
    ],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'proof_screenshot': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_URI),
            'status': openapi.Schema(type=openapi.TYPE_STRING, enum=['P', 'S'], default='P')
        },
        required=['proof_screenshot']
    ),
    responses={
        201: openapi.Response(
            description="Room result entry created successfully.",
            examples={
                'application/json': {
                    "room_id": 1,
                    "user_id": 1,
                    "proof_screenshot": "http://example.com/proof.png",
                    "status": "P"
                }
            }
        ),
        400: openapi.Response(
            description="Invalid input data.",
            examples={
                'application/json': {
                    "proof_screenshot": ["This field is required."]
                }
            }
        ),
        404: openapi.Response(
            description="Room or user not found.",
            examples={
                'application/json': {
                    "error": "Room or user with the given ID not found."
                }
            }
        )
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def create_room_result(request, user_id, room_id):
    try:
        room = Room.objects.get(id=room_id)
    except Room.DoesNotExist:
        return Response({"error": "Room with the given ID not found."}, status=status.HTTP_404_NOT_FOUND)

    try:
        user = get_user_model().objects.get(id=user_id)
    except get_user_model().DoesNotExist:
        return Response({"error": "User with the given ID not found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = RoomResultsSerializer(data=request.data, context={'room': room, 'user': user})

    if serializer.is_valid():
        room_result = serializer.save()
        return Response({
            "room_id": room_result.room.id,
            "user_id": room_result.user.id,
            "proof_screenshot": room_result.proof_screenshot.url if room_result.proof_screenshot else None,
            "status": room_result.status
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)













@swagger_auto_schema(
    method='post',
    operation_description="Join a challenge by providing the user ID and challenge ID.",
    responses={
        200: openapi.Response(
            description="Challenge joined successfully",
            examples={
                "application/json": {
                    "room_id": 1,
                    "challenge_id": "BL123456",
                    "status": "R",
                    "message": "Challenge joined successfully"
                }
            }
        ),
        400: openapi.Response(
            description="Bad request",
            examples={
                "application/json": {
                    "error": "Insufficient balance"
                }
            }
        ),
        403: openapi.Response(
            description="Forbidden",
            examples={
                "application/json": {
                    "error": "User not authenticated or ID mismatch."
                }
            }
        ),
        404: openapi.Response(
            description="Not found",
            examples={
                "application/json": {
                    "error": "Challenge not found"
                },
                "application/json": {
                    "error": "Wallet not found"
                }
            }
        )
    }
)
@api_view(['POST'])
def join_challenge(request, user_id, challenge_id):
    try:
        user = request.user  # Assumes the user is authenticated and available in request
        if not user or user.id != user_id:
            return Response({"error": "User not authenticated or ID mismatch."}, status=status.HTTP_403_FORBIDDEN)

        # Retrieve the challenge
        challenge = get_object_or_404(Challenge, challenge_id=challenge_id)
        room = challenge.room  # Access the room related to the challenge

        # Retrieve the user's wallet
        wallet = get_object_or_404(Wallet, user=user)

        # Check if the user has enough balance
        if wallet.balance < room.room_amount:
            return Response({"error": "Insufficient balance"}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the opponent slot is available
        if not challenge.opponent:
            challenge.opponent = user
        else:
            return Response({"error": "Slots are full"}, status=status.HTTP_400_BAD_REQUEST)

        # Change the status to 'Running' after the opponent has joined
        challenge.status = 'R'
        
        # Save the updated challenge
        challenge.save()
        
        # Deduct the room amount from the user's wallet
        wallet.balance -= room.room_amount
        wallet.save()

        return Response({
            "room_id": room.room_id,
            "challenge_id": challenge.challenge_id,
            "status": challenge.status,
            "message": "Challenge joined successfully"
        }, status=status.HTTP_200_OK)

    except Challenge.DoesNotExist:
        return Response({"error":True,"detail": "Challenge not found"}, status=status.HTTP_404_NOT_FOUND)
    except Wallet.DoesNotExist:
        return Response({"error": True,"detail": "Wallet not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error":True,"detail":  str(e)}, status=status.HTTP_400_BAD_REQUEST)


















@swagger_auto_schema(
    method='get',
    operation_description="Retrieve a list of challenges categorized by their status (open, running, closed) along with details of the created_by and opponent users.",
    responses={
        200: openapi.Response(
            description="Successful Response",
            examples={
                "application/json": {
                    "open_challenges": [
                        {
                            "challenge_id": "BL123456",
                            "room": 1,
                            "created_by": {"id": 1, "username": "user1", "email": "user1@example.com", "first_name": "User", "last_name": "One"},
                            "opponent": {"id": 2, "username": "user2", "email": "user2@example.com", "first_name": "User", "last_name": "Two"},
                            "status": "O"
                        }
                    ],
                    "running_challenges": [],
                    "closed_challenges": []
                }
            }
        )
    }
)
@api_view(['GET'])
@permission_classes([AllowAny])
def list_challenges(request):
    try:
        # Fetch challenges categorized by status
        open_challenges = Challenge.objects.filter(status='O')
        running_challenges = Challenge.objects.filter(status='R')
        closed_challenges = Challenge.objects.filter(status='C')

        # Serialize challenges along with created_by and opponent user details
        open_challenges_data = [
            {
                **ChallengeSerializer(challenge).data,
                'created_by': UserSerializer(challenge.created_by).data,
                'opponent': UserSerializer(challenge.opponent).data if challenge.opponent else None
            } for challenge in open_challenges
        ]
        
        running_challenges_data = [
            {
                **ChallengeSerializer(challenge).data,
                'created_by': UserSerializer(challenge.created_by).data,
                'opponent': UserSerializer(challenge.opponent).data if challenge.opponent else None
            } for challenge in running_challenges
        ]
        
        closed_challenges_data = [
            {
                **ChallengeSerializer(challenge).data,
                'created_by': UserSerializer(challenge.created_by).data,
                'opponent': UserSerializer(challenge.opponent).data if challenge.opponent else None
            } for challenge in closed_challenges
        ]

        return Response({
            "error":False,
            "detail":"Challenges Fetched Successfully",
            "open_challenges": open_challenges_data,
            "running_challenges": running_challenges_data,
            "closed_challenges": closed_challenges_data,
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error":True,"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)