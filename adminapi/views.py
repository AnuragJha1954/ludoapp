from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from .serializers import DepositHistorySerializer, UpdateDepositStatusSerializer, WithdrawalHistorySerializer, UpdateWithdrawalStatusSerializer,RoomResultsSerializer,UpdateRoomResultsStatusSerializer,CommissionPercentageSerializer,WhatsAppNumberSerializer,UPIInfoSerializer, AdminDetailsSerializer
from api.models import DepositHistory,Wallet, WithdrawalHistory, RoomResults, Challenge
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.utils import timezone
from django.db.models import Sum, Count
from django.shortcuts import get_object_or_404
from users.models import AdminDetails
from django.utils.timezone import now
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile



@swagger_auto_schema(
    method='get',
    responses={
        200: openapi.Response(
            description="List of all deposit history entries",
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
def get_all_deposits(request):
    # Fetch all deposits
    all_deposits = DepositHistory.objects.all()
    
    # Separate deposits by status
    pending_deposits = all_deposits.filter(status='P')
    successful_deposits = all_deposits.filter(status='S')

    # Serialize deposits
    pending_deposits_data = DepositHistorySerializer(pending_deposits, many=True, context={'request': request}).data
    successful_deposits_data = DepositHistorySerializer(successful_deposits, many=True, context={'request': request}).data

    return Response({
        "pending_deposits": pending_deposits_data,
        "successful_deposits": successful_deposits_data
    }, status=status.HTTP_200_OK)













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
def update_deposit_status(request, wallet_id, deposit_id):
    # Fetch the wallet using wallet_id
    wallet = get_object_or_404(Wallet, id=wallet_id)
    
    # Fetch the deposit entry using wallet_id and deposit_id
    deposit_entry = get_object_or_404(DepositHistory, id=deposit_id, wallet=wallet)

    if deposit_entry.status == 'S':
        return Response({'message': 'Deposit is already done to the wallet'}, status=status.HTTP_200_OK)

    # Update the deposit status and tag
    deposit_entry.status = 'S'
    deposit_entry.tag = 'D'
    deposit_entry.save()

    # Update the wallet balance
    wallet.balance += deposit_entry.deposit_amount
    wallet.save()

    return Response({'message': 'Deposit Successful and wallet balance updated'}, status=status.HTTP_200_OK)











@swagger_auto_schema(
    method='get',
    responses={
        200: openapi.Response(
            description="List of all withdrawal history entries",
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
def get_all_withdrawals(request):
    # Fetch all withdrawals
    all_withdrawals = WithdrawalHistory.objects.all()
    
    # Separate withdrawals by status
    pending_withdrawals = all_withdrawals.filter(status='P')
    successful_withdrawals = all_withdrawals.filter(status='S')

    # Serialize withdrawals
    pending_withdrawals_data = WithdrawalHistorySerializer(pending_withdrawals, many=True, context={'request': request}).data
    successful_withdrawals_data = WithdrawalHistorySerializer(successful_withdrawals, many=True, context={'request': request}).data

    return Response({
        "pending_withdrawals": pending_withdrawals_data,
        "successful_withdrawals": successful_withdrawals_data
    }, status=status.HTTP_200_OK)










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
def update_withdrawal_status(request, wallet_id, withdrawal_id):
    try:
        # Fetch the wallet and withdrawal entry
        wallet = Wallet.objects.get(id=wallet_id)
        withdrawal_entry = WithdrawalHistory.objects.get(id=withdrawal_id, wallet=wallet)
        
        if withdrawal_entry.status == 'S':
            return Response({'message': 'Withdrawal is already marked as Successful'}, status=status.HTTP_200_OK)

        if wallet.withdrawable_balance < withdrawal_entry.withdrawal_amount:
            return Response({'error': 'Insufficient balance'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        
        # Deduct the withdrawal amount from the wallet's withdrawable balance
        wallet.withdrawable_balance -= withdrawal_entry.withdrawal_amount
        wallet.save()
        
        # Update the withdrawal status
        withdrawal_entry.status = 'S'
        withdrawal_entry.save()
        

        return Response({'message': 'Status updated to Successful and wallet withdrawable balance updated'}, status=status.HTTP_200_OK)
    
    except Wallet.DoesNotExist:
        return Response({'error': 'Wallet not found'}, status=status.HTTP_404_NOT_FOUND)
    except WithdrawalHistory.DoesNotExist:
        return Response({'error': 'Withdrawal not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)












@swagger_auto_schema(
    method='get',
    responses={
        200: openapi.Response(
            description="List of all room results",
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
def get_room_results(request):
    # Fetch room results categorized by status
    pending_results = RoomResults.objects.filter(status='P')
    approved_results = RoomResults.objects.filter(status='A')
    declined_results = RoomResults.objects.filter(status='D')
    
    # Serialize the results
    pending_results_data = RoomResultsSerializer(pending_results, many=True, context={'request': request}).data
    approved_results_data = RoomResultsSerializer(approved_results, many=True, context={'request': request}).data
    declined_results_data = RoomResultsSerializer(declined_results, many=True, context={'request': request}).data
    
    # Return the response
    return Response({
        "pending_results": pending_results_data,
        "approved_results": approved_results_data,
        "declined_results": declined_results_data,
    }, status=status.HTTP_200_OK)













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
def update_room_results_status(request, room_result_id, admin_user_id):
    try:
        room_result = RoomResults.objects.get(id=room_result_id)
        if room_result.status == 'S':
            return Response({'message': 'Room result is already marked as Successful'}, status=status.HTTP_200_OK)
        
        # Get the admin details based on the user ID provided in the URL
        try:
            admin_details = AdminDetails.objects.get(user_id=admin_user_id)
        except AdminDetails.DoesNotExist:
            return Response({'error': 'Admin details not found for the provided user ID'}, status=status.HTTP_404_NOT_FOUND)
        
        # Calculate the commission
        commission_percentage = admin_details.commission_percentage
        commission_amount = (room_result.room.room_amount * commission_percentage) / 100

        # Update the room result with commission amount
        room_result.admin_commission = commission_amount
        room_result.status = 'S'
        room_result.save()

        # Update the wallet balance
        wallet = Wallet.objects.get(user=room_result.user)
        net_amount = room_result.room.room_amount - commission_amount
        wallet.balance += net_amount
        wallet.withdrawable_balance += net_amount
        wallet.save()

        # Create a deposit history entry
        DepositHistory.objects.create(
            wallet=wallet,
            deposit_amount=net_amount,
            proof_screenshot=room_result.proof_screenshot,
            status='S',
            tag='W'
        )

        return Response({'message': 'Room result approved, commission deducted, and wallet updated'}, status=status.HTTP_200_OK)
    except RoomResults.DoesNotExist:
        return Response({'error': 'Room result not found'}, status=status.HTTP_404_NOT_FOUND)
    except Wallet.DoesNotExist:
        return Response({'error': 'Wallet not found for the user'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)








@swagger_auto_schema(
    method='get',
    operation_summary="Get Deposit Summary",
    operation_description="Retrieve the total amount of successful deposits and the amount of successful deposits for the current day.",
    responses={
        200: openapi.Response(
            description="Successful response",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'total_deposits_successful': openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description="Total amount of successful deposits"
                    ),
                    'today_deposits_successful': openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description="Total amount of successful deposits for the current day"
                    ),
                }
            ),
        ),
        500: openapi.Response(
            description="Error response",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'error': openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description="Error message"
                    ),
                    'detail': openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description="Detailed error description"
                    ),
                }
            ),
        ),
    }
)
@api_view(['GET'])
@permission_classes([AllowAny])
def get_deposit_summary(request):
    try:
        # Get the current date and time
        now = timezone.now()
        start_of_today = now.replace(hour=0, minute=0, second=0, microsecond=0)

        # Sum up all deposits (regardless of status)
        upi_total = DepositHistory.objects.aggregate(total=Sum('deposit_amount'))['total'] or 0

        # Sum up deposits for the current day
        today_total = DepositHistory.objects.filter(
            deposit_date__gte=start_of_today
        ).aggregate(total=Sum('deposit_amount'))['total'] or 0

        # Construct the response data
        response_data = {
            "upi_total": str(upi_total),
            "today": str(today_total),
            "admin":str(0)
        }

        return Response({"error":False,"detail": "Deposits retreived successfully",** response_data}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": True, "detail":  str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)














@swagger_auto_schema(
    method='get',
    operation_summary="List Number of Games Status-Wise",
    operation_description="Retrieve the number of challenges grouped by their status.",
    responses={
        200: openapi.Response(
            description="Successful response",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'error': openapi.Schema(
                        type=openapi.TYPE_BOOLEAN,
                        description="Error status"
                    ),
                    'detail': openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description="Detailed success message"
                    ),
                    'status_counts': openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        additional_properties=openapi.Schema(
                            type=openapi.TYPE_INTEGER,
                            description="Count of challenges for each status"
                        ),
                        description="Counts of challenges grouped by status"
                    ),
                }
            ),
        ),
        500: openapi.Response(
            description="Error response",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'error': openapi.Schema(
                        type=openapi.TYPE_BOOLEAN,
                        description="Error status"
                    ),
                    'detail': openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description="Detailed error message"
                    ),
                }
            ),
        ),
    }
)
@api_view(['GET'])
@permission_classes([AllowAny])
def list_challenges_status(request):
    try:
        # Aggregate the number of challenges by status
        status_counts = Challenge.objects.values('status').annotate(count=Count('status'))

        # Map status codes to human-readable labels
        status_mapping = {
            'O': 'open',
            'R': 'running',
            'C': 'closed'
        }

        # Prepare the response data with default counts as 0
        response_data = {'open': 0, 'running': 0, 'closed': 0}
        for entry in status_counts:
            status_key = status_mapping.get(entry['status'])
            if status_key:
                response_data[status_key] = entry['count']

        return Response({
            "error": False,
            "detail": "Challenge counts retrieved successfully",
            ** response_data
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({
            "error": True,
            "detail": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)













@swagger_auto_schema(
    method='get',
    operation_summary="Total Amount of Withdrawals Status-Wise",
    operation_description="Retrieve the total amount of withdrawals grouped by their status.",
    responses={
        200: openapi.Response(
            description="Successful response",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'error': openapi.Schema(
                        type=openapi.TYPE_BOOLEAN,
                        description="Error status"
                    ),
                    'detail': openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description="Detailed success message"
                    ),
                    'status_totals': openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        additional_properties=openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="Total amount of withdrawals for each status"
                        ),
                        description="Total amounts of withdrawals grouped by status"
                    ),
                }
            ),
        ),
        500: openapi.Response(
            description="Error response",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'error': openapi.Schema(
                        type=openapi.TYPE_BOOLEAN,
                        description="Error status"
                    ),
                    'detail': openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description="Detailed error message"
                    ),
                }
            ),
        ),
    }
)
@api_view(['GET'])
@permission_classes([AllowAny])
def total_withdrawals_status(request):
    try:
        # Aggregate the total withdrawal amounts by status
        status_totals = WithdrawalHistory.objects.values('status').annotate(total_amount=Sum('withdrawal_amount'))

        # Prepare the response data
        response_data = {
            "pending": "0.00",
            "successful": "0.00"
        }

        # Map status codes to response keys and update the totals
        for status_total in status_totals:
            if status_total['status'] == 'P':
                response_data['pending'] = str(status_total['total_amount'])
            elif status_total['status'] == 'S':
                response_data['successful'] = str(status_total['total_amount'])

        return Response({
            "error": False,
            "detail": "Total withdrawal amounts retrieved successfully",
            ** response_data
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            "error": True,
            "detail": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)











@swagger_auto_schema(
    method='get',
    operation_description="Get the overall and today's admin commission",
    responses={
        200: openapi.Response(
            description="Successful Response",
            examples={
                "application/json": {
                    "overall_commission": 1500.50,
                    "today_commission": 100.50
                }
            }
        ),
        500: openapi.Response(
            description="Internal Server Error",
            examples={
                "application/json": {
                    "error": "Detailed error message"
                }
            }
        )
    }
)
@api_view(['GET'])
@permission_classes([AllowAny])
def get_admin_commission(request):
    try:
        # Get the current date
        today = now().date()

        # Calculate the overall commission
        overall_commission = RoomResults.objects.aggregate(
            overall_commission=Sum('admin_commission')
        )['overall_commission'] or 0.00

        # Calculate today's commission
        today_commission = RoomResults.objects.filter(timestamp__date=today).aggregate(
            today_commission=Sum('admin_commission')
        )['today_commission'] or 0.00

        return Response({
            'admin': overall_commission,
            'today': today_commission,
            'referal':0
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)





















@swagger_auto_schema(
    method='put',
    operation_description="Change the commission percentage for an admin",
    request_body=CommissionPercentageSerializer,
    responses={
        200: openapi.Response("Commission percentage updated successfully"),
        400: openapi.Response("Invalid input or commission percentage"),
        404: openapi.Response("Admin details not found"),
        500: openapi.Response("Internal server error"),
    }
)
@api_view(['PUT'])
@permission_classes([AllowAny])
def change_commission_percentage(request, user_id):
    try:
        new_percentage = request.data.get('commission_percentage')
        if new_percentage is None:
            return Response(
                {"error": True, "detail": "New commission percentage is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate the new percentage
        try:
            new_percentage = float(new_percentage)
            if new_percentage < 0 or new_percentage > 100:
                return Response(
                    {"error": True, "detail": "Commission percentage must be between 0 and 100"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except ValueError:
            return Response(
                {"error": True, "detail": "Invalid commission percentage"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get the admin details
        admin_details = AdminDetails.objects.get(user_id=user_id)
        admin_details.commission_percentage = new_percentage
        admin_details.save()

        return Response(
            {"success": True, "detail": "Commission percentage updated successfully"},
            status=status.HTTP_200_OK
        )

    except AdminDetails.DoesNotExist:
        return Response(
            {"error": True, "detail": "Admin details not found for the given user ID"},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"error": True, "detail": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        












@swagger_auto_schema(
    method='put',
    operation_description="Update the WhatsApp number for an admin",
    request_body=WhatsAppNumberSerializer,
    responses={
        200: openapi.Response("WhatsApp number updated successfully"),
        400: openapi.Response("Invalid input or WhatsApp number"),
        404: openapi.Response("Admin details not found"),
        500: openapi.Response("Internal server error"),
    }
)
@api_view(['PUT'])
def update_whatsapp_number(request, user_id):
    try:
        whatsapp_number = request.data.get('whatsapp_number')
        if not whatsapp_number:
            return Response(
                {"error": True, "detail": "WhatsApp number is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get the admin details
        admin_details = AdminDetails.objects.get(user_id=user_id)
        admin_details.whatsapp_number = whatsapp_number
        admin_details.save()

        return Response(
            {"success": True, "detail": "WhatsApp number updated successfully"},
            status=status.HTTP_200_OK
        )

    except AdminDetails.DoesNotExist:
        return Response(
            {"error": True, "detail": "Admin details not found for the given user ID"},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"error": True, "detail": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

















@swagger_auto_schema(
    method='post',
    operation_description="Update UPI details and generate QR code",
    request_body=UPIInfoSerializer,
    responses={
        200: openapi.Response("UPI details updated and QR code generated successfully"),
        400: openapi.Response("Invalid input"),
        404: openapi.Response("Admin details not found"),
        500: openapi.Response("Internal server error"),
    }
)
@api_view(['POST'])
def update_upi_details(request, user_id):
    try:
        data = request.data
        upi_name = data.get('upi_name')
        upi_id = data.get('upi_id')

        if not upi_name or not upi_id:
            return Response(
                {"error": True, "detail": "UPI name and UPI ID are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get the admin details
        admin_details = AdminDetails.objects.get(user_id=user_id)

        # Generate UPI QR code
        upi_string = f"upi://pay?pa={upi_id}&pn={upi_name}"
        qr = qrcode.make(upi_string)
        qr_io = BytesIO()
        qr.save(qr_io, format='PNG')
        qr_content = ContentFile(qr_io.getvalue(), name=f"{upi_id}_qr.png")

        # Update admin details
        admin_details.upi_name = upi_name
        admin_details.upi_id = upi_id
        admin_details.upi_qr.save(f"{upi_id}_qr.png", qr_content)
        admin_details.save()

        return Response(
            {"success": True, "detail": "UPI details updated and QR code generated successfully"},
            status=status.HTTP_200_OK
        )

    except AdminDetails.DoesNotExist:
        return Response(
            {"error": True, "detail": "Admin details not found for the given user ID"},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"error": True, "detail": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
















@swagger_auto_schema(
    method='get',
    operation_description="Get Admin details by user ID",
    responses={
        200: AdminDetailsSerializer,
        404: openapi.Response("Admin details not found"),
        500: openapi.Response("Internal server error"),
    }
)
@api_view(['GET'])
def get_admin_details(request, user_id):
    try:
        admin_details = AdminDetails.objects.get(user_id=user_id)
        serializer = AdminDetailsSerializer(admin_details, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    except AdminDetails.DoesNotExist:
        return Response(
            {"error": True, "detail": "Admin details not found for the given user ID"},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"error": True, "detail": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )














