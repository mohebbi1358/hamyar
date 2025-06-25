from django.urls import path
from .views import CondolenceDetailView
from .views import CondolenceListView
from . import views

app_name = 'eternals'

urlpatterns = [
    path('', views.EternalsListView.as_view(), name='list'),
    path('create/', views.EternalsCreateView.as_view(), name='create'),
    path('<int:pk>/', views.EternalsDetailView.as_view(), name='detail'),
    path('<int:eternal_id>/ceremonies/', views.eternal_ceremony_list, name='eternal_ceremonies'),
    path('<int:eternal_id>/ceremonies/add/', views.add_ceremony, name='add_ceremony'),
    path('ceremony/create/', views.CeremonyCreateView.as_view(), name='ceremony_create'),
    path('condolence/create/', views.CondolenceMessageCreateView.as_view(), name='condolence_create'),
    #path('ceremony/<int:pk>/edit/', views.CeremonyUpdateView.as_view(), name='edit_ceremony'),
    #path('ceremony/<int:pk>/delete/', views.CeremonyDeleteView.as_view(), name='delete_ceremony'),
    path('ceremony/<int:pk>/edit/', views.CeremonyUpdateView.as_view(), name='edit_ceremony'),
    path('ceremony/<int:pk>/delete/', views.CeremonyDeleteView.as_view(), name='delete_ceremony'),
    path('<int:eternal_id>/condolences/add/', views.CondolenceMessageCreateView.as_view(), name='add_condolence'),
    path('condolence/create/', views.CondolenceMessageCreateView.as_view(), name='condolence_create'),
    path('condolence/<int:pk>/', CondolenceDetailView.as_view(), name='condolence_detail'),
    path('condolences/<int:eternal_id>/', CondolenceListView.as_view(), name='condolence_list'),




]
