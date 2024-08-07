from django.urls import path
from .views import create_kyc_details,approve_kyc_details,decline_kyc_details,list_kyc_details_by_status


urlpatterns = [
    path('upload/<int:user_id>/', create_kyc_details, name='create_kyc_details'),
    path('approve/<int:user_id>/<int:kyc_id>/', approve_kyc_details, name='approve_kyc_details'),
    path('decline/<int:user_id>/<int:kyc_id>/', decline_kyc_details, name='approve_kyc_details'),
    path('get-kyc/', list_kyc_details_by_status, name='list_kyc_details_by_status'),
]
