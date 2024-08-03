from django.urls import path
from .views import (
    create_deposit,
    create_withdrawal,
    create_room,
    create_wallet,
    create_room_result,
    join_challenge,
    list_challenges
)

urlpatterns = [
    path('create-deposit/<int:wallet_id>/', create_deposit, name='create-deposit'),
    path('create-withdrawal/<int:wallet_id>/', create_withdrawal, name='create-withdrawal'),
    path('create-room/<int:user_id>/', create_room, name='create-room'),
    path('create-wallet/<int:user_id>/', create_wallet, name='create-wallet'),
    path('create-room-result/<int:user_id>/<int:room_id>/', create_room_result, name='create-room-result'),
    path('join-challenge/<int:user_id>/<int:challenge_id>/', join_challenge, name='join_challenge'),
     path('get-challenges/', list_challenges, name='list_challenges'),

]
