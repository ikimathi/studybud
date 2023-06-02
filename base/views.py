# from email import message
# from multiprocessing import context
# from traceback import print_tb
from django.shortcuts import render, redirect

# Create your views here.
from .models import Room, Topic, Message
from .forms import RoomForm
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm

# ROOM INITIALIZED
# rooms = [
#     {'id': 1, 'name':'Lets learn python!'},
#     {'id': 2, 'name':'Design with me'},
#     {'id': 3, 'name':'Frontend developers'},
# ]

# LOGINPAGE VIEW
def loginPage(request):
    page = 'login'
    # EVADES GOING TO THE LOGIN PAGE IF USER IS ALREADY LOGGED IN
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST': # means that user entered their info
    # GET THE USERNAME & PASSWORD AND MAKE THEM LOWERCASE
        username = request.POST.get('username').lower()
        password = request.POST.get('password').lower()
    # CHECK IF USER EXISTS
        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'User does not exist')

    # MAKE SURE CREDENTIALS ARE CORRECT
        user = authenticate(request, username=username, password=password)
    # LOGS A USER IN, CREATES A SESSION_ID AND REDIRECT USER TO THE HOMEPAGE
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'User or Password does not exist')

    context = {'page': page}
    print(context)
    return render(request, 'base/login_register.html', context)

# LOGOUTUSER VIEW
def logoutUser(request):
    logout(request) # DELETE USER/TOKEN
    return redirect('base/login.html')

# REGISTERUSER VIEW
def registerPage(request):
    # DJANGO DEFAULT FORM TEMPLATE
    form = UserCreationForm()

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)  # FREEZE DATA FOR CLEANING BEFORE COMMITING
            user.username = user.username.lower() # MAKE SURE THE USERNAME IS LOWERCASE
            user.save()
            login(request, user) # LOGIN THE USER PASSED IN
            return redirect('home')
        else:
            messages.error(request, 'An error occured during registeration')

    context = {'form': form}
    print(context)
    
    # RETURNS THE SAME TEMPLATE 'LOGIN_REGISTER.HTML'
    return render(request, 'base/login_register.html', context)

# HOME VIEW
def home(request):  # home view
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
    )
    topics = Topic.objects.all()
    room_count = rooms.count() # this works faster than the usual len()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q)) # FILTER BY ROOM TOPIC NAME

    context = {'rooms': rooms, 'topics': topics, 'room_count': room_count, 'room_messages': room_messages} # data to relay on page

    return render(request, 'base/home.html', context)

# ROOM VIEW
def room(request, pk):
    # room = None # ensure there's no duplicate 'room' on top
    # for i in rooms:
    #     if i['id'] == int(pk):
    #         room = i
    room = Room.objects.get(id=pk)  # 'pk' ensures there's no duplicates conflicting
    room_messages = room.message_set.all().order_by('-created') # MANY-TO-ONE RELATIONSHIP
    participants = room.participants.all()    # MANY TO MANY RELATIONSHIP

    if request.method == 'POST':
        message = Message.objects.create(
            user = request.user,
            room = room,
            body = request.POST.get('body') # 'body' FROM TEMPLATE/PAGE
        )

        room.participants.add(request.user) # ADDS A USER AS A PARTICIPANT AFTER POSTING A MESSAGE
        return redirect('room', pk=room.id) # REDIRECTS TO MAKE SURE THE PAGE FUNCTIONS WELL AFTER BEING ALTERED

    context = {'room': room, 'room_messages': room_messages, 'participants': participants} # data to show
    print(context)
    
    return render(request, 'base/room.html', context)

# USERPROFILE VIEW
def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()   # GET ALL THE CHILDREN OF THE OBJECTS OF 'ROOM'
    room_messages = user.message_set.all()   # # GET ALL THE CHILDREN OF THE OBJECTS OF 'room_message'
    topics = Topic.objects.all()

    context = {'user': user, 'rooms': rooms, 'room_messages': room_messages, 'topics': topics}
    return render(request, 'base/profile.html', context)

# CREATEROOM VIEW
@login_required(login_url='login')
def createRoom(request):
    # 'form' PASSED INTO 'room_form.html' as a form template
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == 'POST':
        # print(request.POST)
        form = RoomForm(request.POST)
        if form.is_valid():
        
            room = form.save(commit=False) # SAVE 'ROOMFORM' FIELDS IN TO THE ROOM MODEL(table)
            room.host = request.user    # ROOM HOST IS THE CURRENT USER
            room.save()
            return redirect('home')

    context = {'form': form, 'topics': topics}
    return render(request, 'base/room_form.html', context)

# UPDATEROOM VIEW
@login_required(login_url='login')
def updateRoom(request, pk):    # primarykey, pk -> KNOW WHAT item is getting updated 
    room = Room.objects.get(id=pk)  # get pk by id
    form = RoomForm(instance=room)
    topics = Topic.objects.all()

    # RESTRICT EDITING ANOTHER USER'S ROOM
    if request.user != room.host:
        return HttpResponse('You are not allowed here!')

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()
        # RoomForm(request.POST, instance=room)
        # if form.is_valid():
        #     form.save()
            # return redirect('home')

        return redirect('home')

    context = {'form': form, 'topics': topics}
    return render(request, 'base/room_form.html', context)

# DELETEROOM VIEW
@login_required(login_url='login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)

    # RESTRICT DELETING ANOTHER USER'S ROOM
    if request.user != room.host:
        return HttpResponse('You are not allowed here!')

    if request.method == 'POST':
        room.delete()
        return redirect('home')

    print({'obj': room})

    return render(request, 'base/delete.html', {'obj': room})


# DELETEMESSAGE VIEW
@login_required(login_url='login')
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)

    # RESTRICT DELETING ANOTHER USER'S ROOM
    if request.user != message.user:
        return HttpResponse('Insufficient permissions!')

    if request.method == 'POST':
        message.delete()
        return redirect('home')

    print({'obj': message})

    return render(request, 'base/delete.html', {'obj': message})

@login_required(login_url='login')
def updateUser(request):
    return render(request, 'base/update-user.html')