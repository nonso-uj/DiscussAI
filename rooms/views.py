from django.shortcuts import render, redirect
from django.db.models import Q, Count
from django.urls import reverse
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.serializers import serialize
from django.forms.models import model_to_dict
from django.utils.timesince import timesince
from decouple import config
from huggingface_hub import InferenceClient

from .models import Message, Topic, Room, Summary
from .forms import RoomForm
from userapp.models import User
# Create your views here.

import json

TRIGGER_WORD = '@ai'
MAXIMUM_MESSAGES = 8

# Initialize client for both summarization and chat
client = InferenceClient(token=config("HF_TOKEN"))

def split_text_into_chunks(text, max_chars=1500):
    """
    Safely splits text into chunks by character length for remote summarization.
    Tokens can't be counted without tokenizer, so we go by char length.
    """
    return [text[i:i+max_chars] for i in range(0, len(text), max_chars)]

def q_converter(item):
    role = "assistant" if item.user.first_name == "@ai" else "user"
    return {"role": role, "content": item.content}

def compress_history(text):
    response = client.summarization(text, model="facebook/bart-large-cnn", max_length=150, min_length=50)
    return response[0]["summary_text"]

def ask_ai(query, messages, room):
    msg_len = messages.count()
    prev_messages = list(map(q_converter, messages))
    room_summary = Summary.objects.filter(chatroom=room.id).order_by('-created').first()

    if msg_len > MAXIMUM_MESSAGES and room_summary and room_summary.checks == MAXIMUM_MESSAGES:
        old_text = "\n".join(m["content"] for m in prev_messages)
        chunks = split_text_into_chunks(old_text)
        summaries = [compress_history(chunk) for chunk in chunks]
        summary = compress_history(" ".join(summaries))
        Summary.objects.create(chatroom=room, content=summary, checks=1)
        prev_messages = [{"role": "system", "content": f"Summary so far: {summary}"}]

    elif msg_len > MAXIMUM_MESSAGES and room_summary and room_summary.checks < MAXIMUM_MESSAGES:
        room_summary.checks += 1
        room_summary.save()
        prev_messages = [{"role": "system", "content": f"Summary so far: {room_summary.content}"}] + prev_messages[-6:]

    elif msg_len > MAXIMUM_MESSAGES and room_summary is None:
        old_text = "\n".join(m["content"] for m in prev_messages)
        chunks = split_text_into_chunks(old_text)
        summaries = [compress_history(chunk) for chunk in chunks]
        summary = compress_history(" ".join(summaries))
        Summary.objects.create(chatroom=room, content=summary, checks=1)
        prev_messages = [{"role": "system", "content": f"Summary so far: {summary}"}]

    system_msg = {
        "role": "system",
        "content": (
            "You are an AI bot in this room about "
            f"{room.title} where you provide support, "
            "answer questions and help the discussion, "
            "considering prior messages."
        )
    }

    history = [system_msg] + prev_messages
    history.append({"role": "user", "content": query})

    completion = client.chat.completions.create(
        model="meta-llama/Llama-3.1-8B-Instruct",
        messages=history,
    )

    return completion.choices[0].message.content


def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    
    rooms = Room.objects.filter(Q(topic__title__icontains=q) | Q(title__icontains=q) | Q(description__icontains=q) | Q(host__first_name__icontains=q) | Q(host__last_name__icontains=q)).select_related('host', 'topic').prefetch_related('participants')

    topics = Topic.objects.all().annotate(room_count=Count('room')).prefetch_related('room_set')[:5]

    room_count = rooms.count()

    room_messages = Message.objects.filter(Q(chatroom__topic__title__icontains=q)).select_related('chatroom', 'chatroom__topic').order_by('-created')[:5]

    paginator = Paginator(rooms, 5)
    rooms = paginator.get_page(request.GET.get('page'))

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

    context = {
        'room': room
    }
    return render(request, 'rooms/room.html', context)


def room_messages(request, pk):
    try:
        if request.method == 'POST':
            data = json.loads(request.body)

            if request.user.is_authenticated == False or not request.user:
                return JsonResponse({"success" : False, "response" : "login or register to add a message!"})

            print("data===", data['message'], request.user)
            room_message = data['message']
            if room_message != '' and room_message != None:
                room = Room.objects.get(id=pk)
                msg_qs = room.message_set.select_related('user').order_by('created')

                if TRIGGER_WORD in room_message:
                    ai_reply = ask_ai(room_message, msg_qs, room)

                    if ai_reply:
                        ai_user = User.objects.filter(first_name='@ai').first()
                        Message.objects.bulk_create([
                            Message(user=request.user, content=room_message, chatroom=room),
                            Message(user=ai_user, content=ai_reply, chatroom=room)
                        ])
                    else:
                        return JsonResponse({"success" : False, "response" : "Something went wrong with the ai reply, please try again"})
                else:
                    Message.objects.create(
                        user = request.user,
                        content = room_message,
                        chatroom = room
                    )
                    print('stuff')

                room.participants.add(request.user)
                return JsonResponse({"success" : True, "response" : "message received"})
            else:
                return JsonResponse({"success" : False, "response" : "add a message!"})
    except:
        return JsonResponse({"success" : False, "response" : "An error occured!"})


def get_room_messages(request, pk):
    room = Room.objects.get(id=pk)
    msg_qs = room.message_set.select_related('user').order_by('created')
    messages = [
        {
            "user": {"id": msg.user.id, "first_name": msg.user.first_name},
            "created": timesince(msg.created) + " ago",
            "content": msg.content,
        }
        for msg in msg_qs
    ]
    participants = room.participants.all().order_by('-date_created')
    room_participants = [
        {
            "id": msg.id,
            "first_name": msg.first_name,
        }
        for msg in participants
    ]
    participants_count = room.participants.count()

    return JsonResponse({"success": True, "messages": messages, 'participants': room_participants, 'participants_count': participants_count})


def create_room(request):
    if request.user.is_authenticated == False:
        messages.error(request, 'login or register to create a room!')
        return redirect('login')
    form = RoomForm()
    topics = Topic.objects.all()

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(title=topic_name)

        room = Room.objects.create(
            host = request.user,
            topic = topic,
            title = request.POST.get('title'),
            description = request.POST.get('description')
        )

        ai_user = User.objects.filter(first_name='@ai').first()
        room.participants.add(ai_user)
        room.save()

        Message.objects.create(
            user = ai_user,
            content = 'Hello, I am your AI room assistant here at your service, add "@ai" to your message to ask me anything :)',
            chatroom = room
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
        messages.error(request, "You don't have the appropriate permissions for this!")
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
    print('topics===', topics[0])
    print('room_count===', room_count)

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