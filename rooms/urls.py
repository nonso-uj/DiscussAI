from django.urls import path
from .views import home, create_room, update_room, room_delete, room, topics_page, activity, room_messages, get_room_messages

urlpatterns = [
    path('', home, name='home'),
    path('room/<str:pk>/', room, name='room'),
    path('message/<str:pk>/', room_messages, name='room-messages'),
    path('get-messages/<str:pk>/', get_room_messages, name='get-messages'),
    path('create-room/', create_room, name='create-room'),
    path('topics/', topics_page, name='topics'),
    path('activity/', activity, name='activity'),
    path('update-room/<str:id>/', update_room, name='update-room'),
    path('delete-room/<str:id>/', room_delete, name='delete-room'),
]