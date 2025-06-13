from django.shortcuts import render, redirect
from django.db.models import Q
from django.urls import reverse
from django.contrib import messages
from django.core.paginator import Paginator

from .models import Message, Topic, Room
from .forms import RoomForm
# Create your views here.


def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    rooms = Room.objects.filter(Q(topic__title__icontains=q) | Q(title__icontains=q) | Q(description__icontains=q) | Q(host__first_name__icontains=q) | Q(host__last_name__icontains=q))
    topics = Topic.objects.all()[:5]
    room_count = rooms.count()
    room_messages = Message.objects.filter(Q(chatroom__topic__title__icontains=q)).order_by('-created')[:5]
    paginator = Paginator(rooms, 5)
    page_number = request.GET.get('page')
    rooms = paginator.get_page(page_number)

    context = {
        'rooms': rooms,
        'topics': topics,
        'room_count': room_count,
        'room_messages': room_messages,
        'search_term': q
    }
    return render(request, 'base/home.html', context)


def room(request, pk):
    room = Room.objects.get(id=pk)
    msg = room.message_set.all().order_by('created')
    participants = room.participants.all().order_by('-date_created')

    if request.method == 'POST':
        if request.user.is_authenticated == False:
            messages.error(request, 'login or register to add a message!')
            return redirect(reverse('room', args=[pk]))

        if request.POST['msg'] != '' or request.POST['msg'] != None:
            Message.objects.create(
                user = request.user,
                content = request.POST['msg'],
                chatroom = room
                )
            room.participants.add(request.user)
            return redirect(reverse('room', args=[pk]))
        else:
            messages.error(request, 'add a message!')
            return redirect(reverse('room', args=[pk]))

    context = {
        'room': room,
        'msgs': msg,
        'participants': participants
    }
    return render(request, 'rooms/room.html', context)


def create_room(request):
    if request.user.is_authenticated == False:
        messages.error(request, 'login or register to create a room!')
        return redirect('login')
    form = RoomForm()
    topics = Topic.objects.all()

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(title=topic_name)

        Room.objects.create(
            host = request.user,
            topic = topic,
            title = request.POST.get('title'),
            description = request.POST.get('description')
        )
        messages.success(request, 'Room created successfully!')
        return redirect('home')

    context = {
        'form': form,
        'flag': 'create',
        'topics': topics
    }
    return render(request, 'rooms/create-room.html', context)



def update_room(request, id):
    room = Room.objects.get(id=id)
    form = RoomForm(instance=room)

    if request.user.is_authenticated == False or request.user != room.host:
        return redirect('home')

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(title=topic_name)
        room.topic = topic
        room.title = request.POST.get('title')
        room.description = request.POST.get('description')
        room.save()
        messages.success(request, 'Room updated successfully!')
        return redirect(reverse('room', args=[id]))

    context = {
        'form': form,
        'flag': 'update',
        'room': room
    }
    return render(request, 'rooms/create-room.html', context)
    


def room_delete(request, id):
    room = Room.objects.get(id=id)

    if request.user.is_authenticated == False or request.user != room.host:
        print('redirected sucker')
        return redirect('home')

    if request.method == 'POST':
        room.delete()
        messages.error(request, 'Room deleted!')
        return redirect('home')

    context = {
        'room': room
    }
    return render(request, 'rooms/delete.html', context)



def topics_page(request):
    topics = Topic.objects.all()
    room_count = Room.objects.all().count()

    context = {
        'topics': topics,
        'room_count': room_count,
    }
    return render(request, 'rooms/topics.html', context)



def activity(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    room_messages = Message.objects.filter(Q(chatroom__topic__title__icontains=q) | Q(chatroom__host__id__icontains=q)).order_by('-created')

    context = {
        'room_messages': room_messages,
        'search_term': q
    }
    return render(request, 'rooms/activity.html', context)