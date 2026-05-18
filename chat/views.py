from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import ChatRoom, Message
from orders.models import Order
from django.contrib.auth import get_user_model

User = get_user_model()

@login_required
def chat_list(request):
    rooms = ChatRoom.objects.filter(
        Q(participant1=request.user) | Q(participant2=request.user)
    ).order_by('-updated_at')
    
    valid_rooms = []
    for room in rooms:
        other = room.get_other_user(request.user)
        if other:  # Sirf wahi rooms jahan other exists
            other_name = other.get_full_name()
            if not other_name:
                other_name = other.username
            if not other_name:
                other_name = other.email.split('@')[0]
            
            room.other_user_name = other_name
            room.other_user_obj = other
            room.unread_count = Message.objects.filter(
                room=room, is_read=False
            ).exclude(sender=request.user).count()
            valid_rooms.append(room)
    
    context = {
        'rooms': valid_rooms,
    }
    return render(request, 'chat/chat_list.html', context)

@login_required
def chat_room(request, room_id):
    room = get_object_or_404(ChatRoom, id=room_id)
    
    if request.user not in [room.participant1, room.participant2]:
        messages.error(request, 'Access denied')
        return redirect('chat:chat_list')
    
    # Mark messages as read
    Message.objects.filter(room=room, is_read=False).exclude(sender=request.user).update(is_read=True)
    
    context = {
        'room': room,
        'chat_messages': room.messages.all(),
        'other_user': room.get_other_user(request.user),
    }
    return render(request, 'chat/chat_room.html', context)

@login_required
def start_chat(request, user_id):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    # user_id UUID hai, isliye id se fetch karo
    other_user = get_object_or_404(User, id=user_id)
    
    if request.user == other_user:
        messages.error(request, 'You cannot chat with yourself')
        return redirect('gigs:gig_list')
    
    room = ChatRoom.objects.filter(
        (Q(participant1=request.user) & Q(participant2=other_user)) |
        (Q(participant1=other_user) & Q(participant2=request.user))
    ).first()
    
    if not room:
        room = ChatRoom.objects.create(
            participant1=request.user,
            participant2=other_user
        )
        messages.success(request, f'Chat started with {other_user.get_full_name() or other_user.email}')
    
    return redirect('chat:chat_room', room_id=room.id)
@login_required
def order_chat(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    if request.user not in [order.buyer, order.seller]:
        messages.error(request, 'Access denied')
        return redirect('orders:my_orders')
    
    other_user = order.seller if request.user == order.buyer else order.buyer
    
    room = ChatRoom.objects.filter(
        (Q(participant1=request.user) & Q(participant2=other_user)) |
        (Q(participant1=other_user) & Q(participant2=request.user))
    ).first()
    
    if not room:
        room = ChatRoom.objects.create(
            participant1=request.user,
            participant2=other_user,
            order=order
        )
    
    return redirect('chat:chat_room', room_id=room.id)