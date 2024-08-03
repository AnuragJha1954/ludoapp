from rest_framework import serializers
from .models import Room, Wallet, WithdrawalHistory, DepositHistory, RoomResults,Challenge
from django.contrib.auth import get_user_model


User = get_user_model()

class RoomCreationSerializer(serializers.ModelSerializer):
    number_of_users = serializers.IntegerField()  # Added to accept number of users
    
    class Meta:
        model = Room
        fields = ['room_id', 'room_amount', 'number_of_users']
    
    def create(self, validated_data):
        # Room creation will be handled in the view method
        return validated_data




class WalletCreationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ['balance']  # Only balance is needed as the user is taken from the URL

    def create(self, validated_data):
        user = self.context['user']
        return Wallet.objects.create(user=user, **validated_data)
    
    
    

class DepositHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = DepositHistory
        fields = ['deposit_amount', 'proof_screenshot']
    
    def create(self, validated_data):
        wallet = self.context['wallet']
        return DepositHistory.objects.create(wallet=wallet, **validated_data)
    
    



class WithdrawalHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = WithdrawalHistory
        fields = ['withdrawal_amount', 
            'selected_tab', 
            'account_holder_name', 
            'account_number', 
            'ifsc_code', 
            'upi_id']

    def create(self, validated_data):
        wallet = self.context['wallet']
        return WithdrawalHistory.objects.create(wallet=wallet, **validated_data)
    
    
    



class RoomResultsSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomResults
        fields = ['proof_screenshot']

    def create(self, validated_data):
        room = self.context['room']
        user = self.context['user']
        return RoomResults.objects.create(room=room, user=user, **validated_data)
    
    
    
    


class ChallengeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Challenge
        fields = ['challenge_id', 'room', 'created_by', 'opponent', 'status']
        
        
        
        
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']