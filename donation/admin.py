from django.contrib import admin
from .models import Donation

@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ('id', 'amount', 'cause', 'status', 'ref_id', 'created_at')
    list_filter = ('status', 'cause')
    search_fields = ('ref_id', 'tracking_code')
    readonly_fields = ('created_at', 'gateway_response')
