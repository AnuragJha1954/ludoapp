from django.contrib import admin
from django.urls import path, include
from userauth import views


urlpatterns = [
    path('login', views.user_login, name="Login Method"),
    path('forgot-password/<int:user_id>/', views.forgot_password, name="Forgot Password Method"),
    path('generate-otp/', views.generate_and_send_otp, name='generate_and_send_otp'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    
]
