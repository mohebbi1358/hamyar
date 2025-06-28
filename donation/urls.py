# donation/urls.py
from django.urls import path
from . import views

app_name = 'donation'

urlpatterns = [
    path('donate/martyr/<int:martyr_id>/', views.donate_for_martyr, name='donate_for_martyr'),
    path('donate/', views.donate, name='donate'),
    path('gateway/wallet_charge/<int:wallet_tx_id>/', views.fake_wallet_charge_gateway, name='fake_wallet_charge_gateway'),
    path('gateway/<int:donation_id>/', views.fake_bank_gateway, name='fake_gateway'),
    path('callback/<int:donation_id>/', views.payment_callback, name='payment_callback'),
    path('donate/<int:eternal_id>/', views.donate_for_eternal, name='donate_for_eternal'),
]
