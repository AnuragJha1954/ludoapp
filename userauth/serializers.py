from rest_framework import serializers
from users.models import CustomUser




class CustomUserLoginSerializer(serializers.Serializer):
    username = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('username')
        password = data.get('password')

        if not email or not password:
            raise serializers.ValidationError("Email and password are required.")

        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("Invalid email or password.")

        # Check if the password matches
        if not user.check_password(password):
            raise serializers.ValidationError("Invalid email or password.")

        data['user'] = user
        return data





class ForgotMailSerializer(serializers.Serializer):
    email = serializers.EmailField()
    
    
    





class OTPRequestSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)