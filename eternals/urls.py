from django.urls import path
from . import views
from .views import CondolenceMessageCreateView

app_name = 'eternals'

urlpatterns = [
    path('', views.EternalsListView.as_view(), name='list'),
    path('create/', views.EternalsCreateView.as_view(), name='create'),

    path('<int:pk>/', views.EternalsDetailView.as_view(), name='detail'),
    path('<int:pk>/donations/', views.eternal_donations_list, name='eternal_donations_list'),
    path('<int:pk>/donate/', views.donate_to_eternal, name='donate_to_eternal'),

    path('<int:eternal_id>/ceremonies/', views.eternal_ceremony_list, name='eternal_ceremonies'),
    path('<int:eternal_id>/ceremonies/add/', views.add_ceremony, name='add_ceremony'),
    path('ceremony/create/', views.CeremonyCreateView.as_view(), name='ceremony_create'),
    path('ceremony/<int:pk>/edit/', views.CeremonyUpdateView.as_view(), name='edit_ceremony'),
    path('ceremony/<int:pk>/delete/', views.CeremonyDeleteView.as_view(), name='delete_ceremony'),

    path(
        '<int:eternal_id>/condolences/add/',
        views.CondolenceMessageCreateView.as_view(),
        name='condolence_create'
    ),



    path('condolence/<int:pk>/', views.CondolenceDetailView.as_view(), name='condolence_detail'),
    path('condolences/<int:eternal_id>/', views.CondolenceListView.as_view(), name='condolence_list'),
]
