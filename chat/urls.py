from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.chat_list, name='chat_list'),
    path('room/<uuid:room_id>/', views.chat_room, name='chat_room'),
    path('start/<uuid:user_id>/', views.start_chat, name='start_chat'),  # int se uuid karo
    path('order/<uuid:order_id>/', views.order_chat, name='order_chat'),
]