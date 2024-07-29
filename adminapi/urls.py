from django.urls import path
from .views import get_pending_deposits,update_deposit_status,get_pending_withdrawals,update_withdrawal_status,get_pending_room_results, update_room_results_status

urlpatterns = [
    path('get-deposits/', get_pending_deposits, name='get-pending-deposits'),
    path('approve-deposits/<int:wallet_id>/', update_deposit_status, name='update-deposit-status'),
    path('get-withdrawals/', get_pending_withdrawals, name='get-pending-withdrawals'),
    path('approve-withdrawal/<int:wallet_id>/', update_withdrawal_status, name='update-withdrawal-status'),
    path('get-room-results/', get_pending_room_results, name='get-pending-room-results'),
    path('approve-room-results/<int:room_id>/', update_room_results_status, name='update-room-results-status'),
]
