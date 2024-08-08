from django.urls import path
from .views import get_all_deposits,update_deposit_status,get_all_withdrawals,update_withdrawal_status,get_room_results, update_room_results_status,total_withdrawals_status,get_deposit_summary, list_challenges_status, get_admin_commission, change_commission_percentage, update_whatsapp_number,update_upi_details,get_admin_details,get_challenge_details, list_non_admin_users, admin_deposit

urlpatterns = [
    path('get-deposits/', get_all_deposits, name='get-all-deposits'),
    path('approve-deposits/<int:wallet_id>/<int:deposit_id>/', update_deposit_status, name='update-deposit-status'),
    path('get-withdrawals/', get_all_withdrawals, name='get-pending-withdrawals'),
    path('approve-withdrawal/<int:wallet_id>/<int:withdrawal_id>/', update_withdrawal_status, name='update-withdrawal-status'),
    path('get-room-results/', get_room_results, name='get-room-results'),
    path('approve-room-results/<int:room_id>/<int:admin_user_id>/', update_room_results_status, name='update-room-results-status'),
    path('total-deposits/', get_deposit_summary, name='total_deposits_status'),
    path('number-of-games/', list_challenges_status, name='number_of_games_status'),
    path('total-withdrawals/', total_withdrawals_status, name='total_withdrawals_status'),    
    path('get-commisions/', get_admin_commission, name='get_admin_commission'),    
    path('change-commission/<int:user_id>/', change_commission_percentage, name='change-commission-percentage'),
    path('update-whatsapp-number/<int:user_id>/', update_whatsapp_number, name='update-whatsapp-number'),
    path('update-upi/<int:user_id>/', update_upi_details, name='update-upi-details'),
    path('get-admin-details/<int:user_id>/', get_admin_details, name='get-admin-details'),
    path('get-challenge-details/<str:challenge_id>/', get_challenge_details, name='challenge-details'),
    path('get-users/', list_non_admin_users, name='list-non-admin-users'),
    path('deposit/<int:user_id>/', admin_deposit, name='admin-deposit'),
]
