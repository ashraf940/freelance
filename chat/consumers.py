import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import ChatRoom, Message
from django.contrib.auth import get_user_model

User = get_user_model()

# ✅ SAHI — chat/consumers.py
class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_name']  # ✅ yeh sahi hai
        self.room_group_name = f'chat_{self.room_id}'

        if not self.scope['user'].is_authenticated:
            await self.close()
            return

        if not await self.is_user_in_room(self.scope['user'].id, self.room_id):
            await self.close()
            return

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        user = self.scope['user']
        
        await self.save_message(self.room_id, user.id, message)
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender_id': str(user.id),
                'sender_name': user.get_full_name() or user.email,
            }
        )
    
    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender_id': event['sender_id'],
            'sender_name': event['sender_name'],
        }))
    
    @database_sync_to_async
    def is_user_in_room(self, user_id, room_id):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        try:
            user = User.objects.get(id=user_id)
            room = ChatRoom.objects.get(id=room_id)
            return user in [room.participant1, room.participant2]
        except:
            return False
    
    @database_sync_to_async
    def save_message(self, room_id, user_id, message):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        room = ChatRoom.objects.get(id=room_id)
        user = User.objects.get(id=user_id)
        return Message.objects.create(room=room, sender=user, message=message)