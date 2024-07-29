from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Room, Wallet, WithdrawalHistory, DepositHistory, RoomResults,Challenge
from .serializers import RoomCreationSerializer, WalletCreationSerializer, DepositHistorySerializer, WithdrawalHistorySerializer, RoomResultsSerializer
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
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
            wallet = Wallet.objects.get(user=user)

            # Check if the user has enough balance
            if wallet.balance < validated_data['room_amount']:
                return Response({"error": "Insufficient balance"}, status=status.HTTP_400_BAD_REQUEST)

            # Deduct the room amount from the wallet balance
            wallet.balance -= validated_data['room_amount']
            wallet.save()

            # Create the room
            room = Room.objects.create(user=user, **validated_data)

            # Create the challenge
            Challenge.objects.create(
                room=room,
                created_by=user,
                number_of_users=validated_data.get('number_of_users', 1)
            )

            # Return the details of the created room
            return Response({
                "room_id": room.room_id,
                "user_id": room.user.id,
                "room_amount": room.room_amount
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    except Wallet.DoesNotExist:
        return Response({"error": "Wallet not found"}, status=status.HTTP_404_NOT_FOUND)
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
        return Response({
            "wallet_id": deposit.wallet.id,
            "deposit_amount": str(deposit.deposit_amount),
            "deposit_date": deposit.deposit_date.isoformat(),
            "status": deposit.status,
            "proof_screenshot": deposit.proof_screenshot.url if deposit.proof_screenshot else None
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)








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
        return Response({"error": "Wallet with the given ID not found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = WithdrawalHistorySerializer(data=request.data, context={'wallet': wallet})
    
    if serializer.is_valid():
        withdrawal = serializer.save()
        return Response({
            "wallet_id": withdrawal.wallet.id,
            "withdrawal_amount": str(withdrawal.withdrawal_amount),
            "withdrawal_date": withdrawal.withdrawal_date.isoformat(),
            "status": withdrawal.status
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
    operation_summary="Join a Challenge",
    operation_description="Allows a user to join a challenge if there is an available slot and if the user has sufficient balance.",
    manual_parameters=[
        openapi.Parameter('user_id', openapi.IN_PATH, description="ID of the user joining the challenge", type=openapi.TYPE_INTEGER),
        openapi.Parameter('challenge_id', openapi.IN_PATH, description="ID of the challenge to join", type=openapi.TYPE_INTEGER),
    ],
    responses={
        200: openapi.Response(
            description="Challenge joined successfully",
            examples={
                'application/json': {
                    "room_id": 1,
                    "message": "Challenge joined successfully"
                }
            }
        ),
        400: openapi.Response(
            description="Bad Request",
            examples={
                'application/json': {
                    "error": "Insufficient balance"
                }
            }
        ),
        403: openapi.Response(
            description="Forbidden",
            examples={
                'application/json': {
                    "error": "User not authenticated or ID mismatch."
                }
            }
        ),
        404: openapi.Response(
            description="Not Found",
            examples={
                'application/json': {
                    "error": "Challenge not found"
                }
            }
        ),
    }
)
@api_view(['POST'])
def join_challenge(request, user_id, challenge_id):
    try:
        user = request.user  # Assumes the user is authenticated and available in request
        if not user or user.id != user_id:
            return Response({"error": "User not authenticated or ID mismatch."}, status=status.HTTP_403_FORBIDDEN)
        
        # Retrieve the challenge
        challenge = get_object_or_404(Challenge, id=challenge_id)
        room = challenge.room  # Access the room related to the challenge

        # Retrieve the user's wallet
        wallet = get_object_or_404(Wallet, user=user)
        
        # Check if the user has enough balance
        if wallet.balance < room.room_amount:
            return Response({"error": "Insufficient balance"}, status=status.HTTP_400_BAD_REQUEST)

        # Check challenge slots and assign the user
        if not challenge.user1:
            challenge.user1 = user
        elif not challenge.user2:
            challenge.user2 = user
        elif not challenge.user3:
            challenge.user3 = user
        else:
            return Response({"error": "Slots are full"}, status=status.HTTP_400_BAD_REQUEST)

        # Save the updated challenge
        challenge.save()
        
        # Deduct the room amount from the user's wallet
        wallet.balance -= room.room_amount
        wallet.save()
        
        return Response({
            "room_id": room.room_id,
            "message": "Challenge joined successfully"
        }, status=status.HTTP_200_OK)

    except Challenge.DoesNotExist:
        return Response({"error": "Challenge not found"}, status=status.HTTP_404_NOT_FOUND)
    except Wallet.DoesNotExist:
        return Response({"error": "Wallet not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


