from django.urls import path
from .views import user_login, user_register, user_logout, user_profile, user_edit, updateProfile

urlpatterns = [
    path('login/', user_login, name='login'),
    path('register/', user_register, name='register'),
    path('user-edit/', updateProfile, name='user-edit'),
    path('settings/', user_edit, name='settings'),
    path('logout/', user_logout, name='logout'),
    path('profile/<str:pk>/', user_profile, name='profile'),
]