from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Q
from django.urls import reverse

from rooms.models import Message, Room, Topic
from users.models import Profile
from django.contrib.auth import get_user_model
from .forms import CustomUserCreationForm, UpdateProfileForm, UserEditForm
# Create your views here.


def user_login(request):
    if request.user.is_authenticated == True:
        return redirect('home')
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Login successfull!')
            return redirect('home')
        else:
            messages.error(request, 'Incorrect username or password!')
            return redirect('login')
        
    return render(request, 'users/login.html')


def user_register(request):
    if request.user.is_authenticated == True:
        return redirect('home')
    form = CustomUserCreationForm()
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.first_name = user.first_name.lower()
            user.last_name = user.last_name.lower()
            user.save()
            profile = get_user_model().objects.get(email=user.email)
            Profile.objects.create(user=profile)
            messages.success(request, 'Account created successfully!')
            return redirect('login')
        else:
            messages.error(request, 'Something went wrong, try again!')
            return redirect('register')

    context ={
        'form': form,
        'flag': 'register'
    }
    return render(request, 'users/registration.html', context)


def user_edit(request):
    if request.user.is_authenticated == False:
        return redirect('home')
    form = UserEditForm(instance=request.user)
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=request.user)
        print(form)
        if form.is_valid():
            user = form.save(commit=False)
            user.first_name = user.first_name.lower()
            user.last_name = user.last_name.lower()
            user.save()
            messages.success(request, 'Account updated successfully!')
            return redirect(reverse('profile', args=[request.user.id]))
        else:
            messages.error(request, 'Something went wrong, try again!')
            return redirect(reverse('profile', args=[request.user.id]))

    context ={
        'form': form,
        'flag': 'edit'
    }
    return render(request, 'users/registration.html', context)


def user_logout(request):
    logout(request)
    return redirect('login')



def user_profile(request, pk):
    topics = Topic.objects.all()
    user = get_user_model().objects.get(id=pk)
    room_count = Room.objects.all().count()
    # rooms = user.room_set.all()
    rooms = Room.objects.filter(Q(host=user) | Q(participants__in=[user]))
    room_messages = user.message_set.all()
    search_term = user.id
    context = {
        'user': user,
        'rooms': rooms,
        'topics': topics,
        'room_count': room_count,
        'room_messages': room_messages,
        'search_term': user.id
    }
    return render(request, 'users/profile.html', context)



def updateProfile(request):
    profile = Profile.objects.get(user=request.user)
    form = UpdateProfileForm(instance=profile)

    if request.method == 'POST':
        form = UpdateProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect(reverse('profile', args=[request.user.id]))
        else:
            messages.error(request, 'Something went wrong, try again!')
            return redirect(reverse('profile', args=[request.user.id]))
    
    context = {
        'form': form,
        'profile': profile
    }
    return render(request, 'users/edit-profile.html', context)
            