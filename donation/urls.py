# donation/urls.py
from django.urls import path
from . import views
from django.urls import path
from . import views
from .views import UserDonationListView


app_name = 'donation'

urlpatterns = [
    path('my-donations/', UserDonationListView.as_view(), name='user_donation_list'),

    path('detail/<int:pk>/', views.donation_detail, name='donation_detail'),

    path('reports/', views.donation_wallet_report, name='donation_wallet_report'),

    path('causes/', views.donationcause_list, name='donationcause_list'),
    path('causes/add/', views.donationcause_create, name='donationcause_create'),
    path('causes/<int:pk>/edit/', views.donationcause_edit, name='donationcause_edit'),
    path('causes/<int:pk>/delete/', views.donationcause_delete, name='donationcause_delete'),

    path('donate/martyr/<int:martyr_id>/', views.donate_for_martyr, name='donate_for_martyr'),
    path('donate/', views.donate, name='donate'),
    path('gateway/wallet_charge/<int:wallet_tx_id>/', views.fake_wallet_charge_gateway, name='fake_wallet_charge_gateway'),
    path('gateway/<int:donation_id>/', views.fake_bank_gateway, name='fake_gateway'),
    path('callback/<int:donation_id>/', views.payment_callback, name='payment_callback'),
    path('donate/<int:eternal_id>/', views.donate_for_eternal, name='donate_for_eternal'),
]
