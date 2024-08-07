from rest_framework import serializers
from api.models import DepositHistory, WithdrawalHistory, RoomResults
from users.models import AdminDetails


class DepositHistorySerializer(serializers.ModelSerializer):
    proof_screenshot_url = serializers.SerializerMethodField()

    class Meta:
        model = DepositHistory
        fields = ['id', 'wallet', 'deposit_amount', 'deposit_date', 'status', 'proof_screenshot', 'proof_screenshot_url']
        depth = 1  # To include nested serialization of the wallet and user details if needed

    def get_proof_screenshot_url(self, obj):
        request = self.context.get('request')
        if obj.proof_screenshot and hasattr(obj.proof_screenshot, 'url'):
            return request.build_absolute_uri(obj.proof_screenshot.url)
        return None




class UpdateDepositStatusSerializer(serializers.Serializer):
    deposit_date = serializers.DateTimeField()
    
    class Meta:
        fields = ['deposit_date']
        





class WithdrawalHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = WithdrawalHistory
        fields = ['id', 'wallet', 'withdrawal_amount', 'withdrawal_date', 'status']
        depth = 1  # To include nested serialization of the wallet and user details if needed







class UpdateWithdrawalStatusSerializer(serializers.Serializer):
    withdrawal_date = serializers.DateTimeField()
    
    class Meta:
        fields = ['withdrawal_date']






class RoomResultsSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomResults
        fields = ['id', 'room', 'user', 'proof_screenshot', 'status']
        depth = 1  # To include nested serialization of the room and user details if needed







class UpdateRoomResultsStatusSerializer(serializers.Serializer):
    class Meta:
        fields = []






class CommissionPercentageSerializer(serializers.Serializer):
    commission_percentage = serializers.DecimalField(max_digits=5, decimal_places=2)








class WhatsAppNumberSerializer(serializers.Serializer):
    whatsapp_number = serializers.CharField(max_length=15)




class UPIInfoSerializer(serializers.Serializer):
    upi_name = serializers.CharField(max_length=255)
    upi_id = serializers.CharField(max_length=255)






class AdminDetailsSerializer(serializers.ModelSerializer):
    upi_qr_url = serializers.SerializerMethodField()

    class Meta:
        model = AdminDetails
        fields = ['user', 'commission_percentage', 'upi_name', 'upi_id', 'upi_qr_url']

    def get_upi_qr_url(self, obj):
        request = self.context.get('request')
        if obj.upi_qr and hasattr(obj.upi_qr, 'url'):
            return request.build_absolute_uri(obj.upi_qr.url)
        return None


