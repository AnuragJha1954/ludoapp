from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, schema
from rest_framework.permissions import AllowAny
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.contrib.auth import get_user_model
from .models import KYCDetails
from .serializers import KYCDetailsSerializer




@swagger_auto_schema(
    method='post',
    request_body=KYCDetailsSerializer,
    responses={
        201: openapi.Response('KYC details submitted successfully', KYCDetailsSerializer),
        400: 'Invalid input',
        404: 'User not found'
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def create_kyc_details(request, user_id):
    try:
        User = get_user_model()
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = KYCDetailsSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=user)
        return Response({
            "error": False,
            "detail": "KYC details submitted successfully",
            "kyc_details": serializer.data
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)












@swagger_auto_schema(
    method='post',
    responses={
        200: openapi.Response('KYC details approved successfully'),
        400: 'Invalid input',
        404: 'User or KYC details not found'
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def approve_kyc_details(request, user_id, kyc_id):
    try:
        User = get_user_model()
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    try:
        kyc_details = KYCDetails.objects.get(id=kyc_id, user=user)
    except KYCDetails.DoesNotExist:
        return Response({"error": "KYC details not found"}, status=status.HTTP_404_NOT_FOUND)

    kyc_details.status = 'A'  # Assuming 'A' stands for 'Approved'
    kyc_details.save()
    
    # Set the user's KYC field to True
    user.kyc = True
    user.save()

    return Response({
        "error": False,
        "detail": "KYC details approved successfully",
        "kyc_details": KYCDetailsSerializer(kyc_details).data
    }, status=status.HTTP_200_OK)













@swagger_auto_schema(
    method='post',
    responses={
        200: openapi.Response('KYC details declined successfully'),
        400: 'Invalid input',
        404: 'User or KYC details not found'
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def decline_kyc_details(request, user_id, kyc_id):
    try:
        User = get_user_model()
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    try:
        kyc_details = KYCDetails.objects.get(id=kyc_id, user=user)
    except KYCDetails.DoesNotExist:
        return Response({"error": "KYC details not found"}, status=status.HTTP_404_NOT_FOUND)

    kyc_details.status = 'D'  # Assuming 'A' stands for 'Approved'
    kyc_details.save()
    
    # Set the user's KYC field to True
    user.kyc = False
    user.save()

    return Response({
        "error": False,
        "detail": "KYC details approved successfully",
        "kyc_details": KYCDetailsSerializer(kyc_details).data
    }, status=status.HTTP_200_OK)















@swagger_auto_schema(
    method='get',
    responses={
        200: openapi.Response('Successfully fetched KYC details', KYCDetailsSerializer(many=True)),
        400: 'Invalid input',
    }
)
@api_view(['GET'])
@permission_classes([AllowAny])
def list_kyc_details_by_status(request):
    try:
        # Fetch KYC details categorized by status
        pending_kyc = KYCDetails.objects.filter(status='P')
        approved_kyc = KYCDetails.objects.filter(status='A')
        declined_kyc = KYCDetails.objects.filter(status='D')

        # Serialize the KYC details
        pending_kyc_data = KYCDetailsSerializer(pending_kyc, many=True).data
        approved_kyc_data = KYCDetailsSerializer(approved_kyc, many=True).data
        declined_kyc_data = KYCDetailsSerializer(declined_kyc, many=True).data

        return Response({
            "error": False,
            "detail": "KYC details fetched successfully",
            "pending_kyc": pending_kyc_data,
            "approved_kyc": approved_kyc_data,
            "declined_kyc": declined_kyc_data,
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": True, "detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)













