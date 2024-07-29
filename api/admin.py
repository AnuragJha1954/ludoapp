from django.contrib import admin
from .models import Wallet, DepositHistory, WithdrawalHistory, Room,Challenge

# Register your models here.
class WalletAdmin(admin.ModelAdmin):
    list_display = ['user', 'balance', 'last_modified']

class DepositHistoryAdmin(admin.ModelAdmin):
    list_display = ['wallet', 'deposit_amount', 'deposit_date', 'status']

class WithdrawalHistoryAdmin(admin.ModelAdmin):
    list_display = ['wallet', 'withdrawal_amount', 'withdrawal_date', 'status']

class RoomAdmin(admin.ModelAdmin):
    list_display = ['room_id', 'user', 'room_amount']


admin.site.register(Wallet, WalletAdmin)
admin.site.register(DepositHistory, DepositHistoryAdmin)
admin.site.register(WithdrawalHistory, WithdrawalHistoryAdmin)
admin.site.register(Room, RoomAdmin)
admin.site.register(Challenge)