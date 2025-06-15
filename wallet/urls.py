from django.urls import path
from . import views

app_name = 'wallet'

urlpatterns = [
    # کیف پول - داشبورد و گزارش
    path('dashboard/', views.wallet_dashboard, name='wallet_dashboard'),
    path('report/', views.wallet_transactions_report, name='wallet_transactions_report'),
    

    # شارژ کیف پول
    path('charge/', views.charge_wallet, name='charge_wallet'),
    path('charge/callback/<int:wallet_tx_id>/', views.wallet_charge_callback, name='wallet_charge_callback'),
    path('gateway/fake_charge/<int:wallet_tx_id>/', views.fake_wallet_charge_gateway, name='fake_wallet_charge_gateway'),

    # پرداخت صدقه از کیف پول
    path('donate/', views.donate_from_wallet, name='donate_from_wallet'),
    
    
]
