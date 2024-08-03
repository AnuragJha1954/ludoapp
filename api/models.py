from django.db import models
from django.conf import settings
from django.utils import timezone


# Create your models here.


class Wallet(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    last_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Wallet of {self.user.username} with balance {self.balance}"
    
    
    
    
    
class DepositHistory(models.Model):
    STATUS_CHOICES = [
        ('P', 'Pending'),
        ('S', 'Successful'),
    ]

    wallet = models.ForeignKey('Wallet', on_delete=models.CASCADE)
    deposit_amount = models.DecimalField(max_digits=10, decimal_places=2)
    deposit_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='P')
    proof_screenshot = models.ImageField(upload_to='deposits/', null=True, blank=True)

    def __str__(self):
        return f"Deposit of {self.deposit_amount} to {self.wallet.user.username} on {self.deposit_date}"    
    





class WithdrawalHistory(models.Model):
    STATUS_CHOICES = [
        ('P', 'Pending'),
        ('S', 'Successful'),
    ]

    wallet = models.ForeignKey('Wallet', on_delete=models.CASCADE)
    withdrawal_amount = models.DecimalField(max_digits=10, decimal_places=2)
    withdrawal_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='P')
    selected_tab = models.CharField(max_length=50, null=True, blank=True)
    account_holder_name = models.CharField(max_length=100, null=True, blank=True)
    account_number = models.CharField(max_length=50, null=True, blank=True)
    ifsc_code = models.CharField(max_length=11, null=True, blank=True)
    upi_id = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f"Withdrawal of {self.withdrawal_amount} from {self.wallet.user.username} on {self.withdrawal_date}"





class Room(models.Model):
    room_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    room_amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Room {self.room_id} for user {self.user.username} with amount {self.room_amount}"
    
    
    
    




class RoomResults(models.Model):
    STATUS_CHOICES = [
        ('P', 'Pending'),
        ('S', 'Successful'),
    ]
    room = models.ForeignKey('Room', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    proof_screenshot = models.ImageField(upload_to='winnings/', null=True, blank=True)
    challenge = models.ForeignKey('Challenge', on_delete=models.CASCADE)  # Added ForeignKey to Challenge
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='P')

    def __str__(self):
        return f"Winner of Room {self.room_id} is user {self.user.username}"
    
    




class Challenge(models.Model):
    STATUS_CHOICES = [
        ('O', 'Open'),
        ('R', 'Running'),
        ('C', 'Closed'),
    ]

    challenge_id = models.CharField(max_length=10, primary_key=True)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_challenges')
    opponent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='opponent_challenges', null=True, blank=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='O')

    def __str__(self):
        return f"Challenge {self.challenge_id} in Room {self.room.room_id} created by {self.created_by.username}"