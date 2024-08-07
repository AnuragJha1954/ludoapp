from rest_framework import serializers
from .models import KYCDetails

class KYCDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = KYCDetails
        fields = ['full_name', 'document_number', 'front_side', 'back_side', 'status']
        read_only_fields = ['status']

    def create(self, validated_data):
        # Set the status to 'Pending' by default
        validated_data['status'] = 'P'
        return super().create(validated_data)
