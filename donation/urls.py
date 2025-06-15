# donation/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('donate/', views.donate, name='donate'),
    path('gateway/wallet_charge/<int:wallet_tx_id>/', views.fake_wallet_charge_gateway, name='fake_wallet_charge_gateway'),
    path('gateway/<int:donation_id>/', views.fake_bank_gateway, name='fake_gateway'),  # مسیر درگاه پرداخت
    path('callback/<int:donation_id>/', views.payment_callback, name='payment_callback'),  # مسیر کال‌بک پرداخت
    
]
