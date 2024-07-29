from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from .serializers import DepositHistorySerializer, UpdateDepositStatusSerializer, WithdrawalHistorySerializer, UpdateWithdrawalStatusSerializer,RoomResultsSerializer,UpdateRoomResultsStatusSerializer
from api.models import DepositHistory,Wallet, WithdrawalHistory, RoomResults
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

@swagger_auto_schema(
    method='get',
    responses={
        200: openapi.Response(
            description="List of pending deposit history entries",
            schema=openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'wallet': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                'user': openapi.Schema(
                                    type=openapi.TYPE_OBJECT,
                                    properties={
                                        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                        'username': openapi.Schema(type=openapi.TYPE_STRING),
                                        # Add other user fields if needed
                                    }
                                ),
                                'balance': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DECIMAL),
                                'last_modified': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
                            }
                        ),
                        'deposit_amount': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DECIMAL),
                        'deposit_date': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
                        'status': openapi.Schema(type=openapi.TYPE_STRING, enum=['P', 'S']),
                        'proof_screenshot': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_URI),
                        'proof_screenshot_url': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_URI),
                    }
                )
            )
        ),
        400: openapi.Response(description="Bad request"),
    }
)
@api_view(['GET'])
@permission_classes([AllowAny])
def get_pending_deposits(request):
    pending_deposits = DepositHistory.objects.filter(status='P')
    serializer = DepositHistorySerializer(pending_deposits, many=True, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)








@swagger_auto_schema(
    method='put',
    request_body=UpdateDepositStatusSerializer,
    responses={
        200: 'Status updated to Successful',
        400: 'Bad request',
        404: 'Deposit not found',
    }
)
@api_view(['PUT'])
@permission_classes([AllowAny])
def update_deposit_status(request, wallet_id):
    serializer = UpdateDepositStatusSerializer(data=request.data)
    if serializer.is_valid():
        deposit_date = serializer.validated_data['deposit_date']
        try:
            deposit_entry = DepositHistory.objects.get(wallet_id=wallet_id, deposit_date=deposit_date)
            deposit_entry.status = 'S'
            deposit_entry.save()
            return Response({'message': 'Status updated to Successful'}, status=status.HTTP_200_OK)
        except DepositHistory.DoesNotExist:
            return Response({'error': 'Deposit not found'}, status=status.HTTP_404_NOT_FOUND)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)











@swagger_auto_schema(
    method='put',
    request_body=UpdateDepositStatusSerializer,
    responses={
        200: 'Status updated to Successful and wallet balance updated',
        400: 'Bad request',
        404: 'Deposit not found',
    }
)
@api_view(['PUT'])
@permission_classes([AllowAny])
def update_deposit_status(request, wallet_id):
    serializer = UpdateDepositStatusSerializer(data=request.data)
    if serializer.is_valid():
        deposit_date = serializer.validated_data['deposit_date']
        try:
            deposit_entry = DepositHistory.objects.get(wallet_id=wallet_id, deposit_date=deposit_date)
            if deposit_entry.status == 'S':
                return Response({'message': 'Deposit is already marked as Successful'}, status=status.HTTP_200_OK)
            
            deposit_entry.status = 'S'
            deposit_entry.save()

            # Update the wallet balance
            wallet = deposit_entry.wallet
            wallet.balance += deposit_entry.deposit_amount
            wallet.save()

            return Response({'message': 'Status updated to Successful and wallet balance updated'}, status=status.HTTP_200_OK)
        except DepositHistory.DoesNotExist:
            return Response({'error': 'Deposit not found'}, status=status.HTTP_404_NOT_FOUND)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)












@swagger_auto_schema(
    method='get',
    responses={
        200: openapi.Response(
            description="List of pending withdrawal history entries",
            schema=openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'wallet': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                'user': openapi.Schema(
                                    type=openapi.TYPE_OBJECT,
                                    properties={
                                        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                        'username': openapi.Schema(type=openapi.TYPE_STRING),
                                        # Add other user fields if needed
                                    }
                                ),
                                'balance': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DECIMAL),
                                'last_modified': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
                            }
                        ),
                        'withdrawal_amount': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DECIMAL),
                        'withdrawal_date': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
                        'status': openapi.Schema(type=openapi.TYPE_STRING, enum=['P', 'S']),
                    }
                )
            )
        ),
        400: openapi.Response(description="Bad request"),
    }
)
@api_view(['GET'])
@permission_classes([AllowAny])
def get_pending_withdrawals(request):
    pending_withdrawals = WithdrawalHistory.objects.filter(status='P')
    serializer = WithdrawalHistorySerializer(pending_withdrawals, many=True, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)










@swagger_auto_schema(
    method='put',
    request_body=UpdateWithdrawalStatusSerializer,
    responses={
        200: 'Status updated to Successful and wallet balance updated',
        400: 'Bad request',
        404: 'Withdrawal not found',
        422: 'Insufficient balance'
    }
)
@api_view(['PUT'])
@permission_classes([AllowAny])
def update_withdrawal_status(request, wallet_id):
    serializer = UpdateWithdrawalStatusSerializer(data=request.body)
    if serializer.is_valid():
        withdrawal_date = serializer.validated_data['withdrawal_date']
        try:
            withdrawal_entry = WithdrawalHistory.objects.get(wallet_id=wallet_id, withdrawal_date=withdrawal_date)
            if withdrawal_entry.status == 'S':
                return Response({'message': 'Withdrawal is already marked as Successful'}, status=status.HTTP_200_OK)
            
            wallet = withdrawal_entry.wallet
            if wallet.balance < withdrawal_entry.withdrawal_amount:
                return Response({'error': 'Insufficient balance'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            
            # Update the withdrawal status
            withdrawal_entry.status = 'S'
            withdrawal_entry.save()
            
            # Update the wallet balance
            wallet.balance -= withdrawal_entry.withdrawal_amount
            wallet.save()

            return Response({'message': 'Status updated to Successful and wallet balance updated'}, status=status.HTTP_200_OK)
        except WithdrawalHistory.DoesNotExist:
            return Response({'error': 'Withdrawal not found'}, status=status.HTTP_404_NOT_FOUND)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)













@swagger_auto_schema(
    method='get',
    responses={
        200: openapi.Response(
            description="List of pending room results",
            schema=openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'room': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                'room_amount': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DECIMAL),
                                'user': openapi.Schema(
                                    type=openapi.TYPE_OBJECT,
                                    properties={
                                        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                        'username': openapi.Schema(type=openapi.TYPE_STRING),
                                        # Add other user fields if needed
                                    }
                                ),
                            }
                        ),
                        'user': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                'username': openapi.Schema(type=openapi.TYPE_STRING),
                                # Add other user fields if needed
                            }
                        ),
                        'proof_screenshot': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_URI),
                        'status': openapi.Schema(type=openapi.TYPE_STRING, enum=['P', 'S']),
                    }
                )
            )
        ),
        400: openapi.Response(description="Bad request"),
    }
)
@api_view(['GET'])
@permission_classes([AllowAny])
def get_pending_room_results(request):
    pending_results = RoomResults.objects.filter(status='P')
    serializer = RoomResultsSerializer(pending_results, many=True, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)













@swagger_auto_schema(
    method='put',
    request_body=UpdateRoomResultsStatusSerializer,
    responses={
        200: 'Status updated to Successful and wallet balance updated',
        400: 'Bad request',
        404: 'Room result not found',
    }
)
@api_view(['PUT'])
@permission_classes([AllowAny])
def update_room_results_status(request, room_id):
    try:
        room_result = RoomResults.objects.get(room_id=room_id)
        if room_result.status == 'S':
            return Response({'message': 'Room result is already marked as Successful'}, status=status.HTTP_200_OK)

        room_amount = room_result.room.room_amount
        wallet = Wallet.objects.get(user=room_result.user)
        
        # Update the room result status
        room_result.status = 'S'
        room_result.save()
        
        # Update the wallet balance
        wallet.balance += room_amount
        wallet.save()

        return Response({'message': 'Status updated to Successful and wallet balance updated'}, status=status.HTTP_200_OK)
    except RoomResults.DoesNotExist:
        return Response({'error': 'Room result not found'}, status=status.HTTP_404_NOT_FOUND)
    except Wallet.DoesNotExist:
        return Response({'error': 'Wallet not found'}, status=status.HTTP_404_NOT_FOUND)











