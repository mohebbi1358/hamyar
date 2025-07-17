from django.urls import path
from . import views
#from .views import CompleteProfileView
from django.urls import path

from .views import login_view, verify_view, CompleteProfileView,logout_view

app_name = 'accounts'

urlpatterns = [
    path('api/search/', views.user_search, name='user_search'),

    #path('complete-profile/', CompleteProfileView.as_view()),
    path('login/', login_view, name='login'),
    
    path('verify/', verify_view, name='verify'),
    
    path('complete-profile/', CompleteProfileView.as_view(), name='complete_profile'),
    
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('logout/', logout_view, name='logout'),
    path('assign-categories/<int:user_id>/', views.assign_categories_to_user, name='assign_categories'),
    path('user-list/', views.user_list, name='user_list'),
    path('manage-personas/<int:user_id>/', views.manage_user_personas, name='manage_personas'),
    
    path('persona/edit/<int:persona_id>/', views.edit_persona, name='edit_persona'),
    path('persona/delete/<int:persona_id>/', views.delete_persona, name='delete_persona'),

    

    
]
