from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from pusher import Pusher
from django.http import JsonResponse
from django.http import HttpResponseForbidden
from decouple import config
from django.contrib.auth.models import User
from .models import *
from rest_framework.decorators import api_view
import json
from util.sample_generator import World,vector2;
import random;
from threading import Timer
# instantiate pusher
# pusher = Pusher(app_id=config('PUSHER_APP_ID'), key=config('PUSHER_KEY'), secret=config('PUSHER_SECRET'), cluster=config('PUSHER_CLUSTER'))
world = []
global winner;

winner = None;
def build_world():
    global winner;
    for i in range(len(world)):
        world.pop();
    for i in range(1):
            w = World()
            num_rooms = 1000
            width = int(2**(5+(i*0.5)));
            height = int(2**(4+(i*0.5)));
            w.generate_rooms(width, height, num_rooms, random.randint(width//4, (3*width)//4),random.randint(height//4, (3*height)//4), 999);
            #w.print_rooms(); 
            world.append(w);
    players =Player.objects.all();
    for a in players:
        if(a.last_update > 0):
            a.x = world[0].home.x+random.randint(-2,2);
            a.y = world[0].home.y+random.randint(-2,2);
            a.z = 0;
        else:
            a.x = -1;
            a.y = -1;
            a.z = -1;
        a.save();
    winner = None;
build_world();

def authorize_user(user):
    try:
        return user.player 
    except: #player is not logged in
        return None;
def setwinner(player):
    winner = player;

@csrf_exempt
@api_view(["GET"])
def initialize(request):
    user = request.user
    player = authorize_user(user);
    if(player==None):
        return  JsonResponse({'error': 'unauthorized access', 'message': 'please login before accessing this page'},safe=True);
    if(player.x < 0 or player.y < 0 or player.z < 0):
        player.x = world[0].home.x + random.randint(-2,2);
        player.y = world[0].home.y + random.randint(-2,2);
        player.z = 0;
        player.save();
    return JsonResponse({ \
        'uuid': player.uuid,\
        'curpos': {'x': player.x, 'y': player.y, 'z': player.z }, \
        'map': { \
            'lvl': 1, \
            'size': {
                'width': len(world[player.z].grid[0]), \
                'height': len(world[player.z].grid)\
            }, \
            'data': world[player.z].grid \
        } \
    }, safe=True);
    #player_id = player.id
    #uuid = player.uuid
    #room = player.room()
    #players = room.playerNames(player_id)
    #return JsonResponse({'uuid': uuid, 'name':player.user.username, 'title':room.title, 'description':room.description, 'players':players, 'map': [i.grid for i in world]}, safe=True)

def createWelcomePacket(player, spawn): #welcome packet sends the player the map and all the player info again so they know every thing they need to know
    #spawn player 
    if(spawn == True):
        player.x = world[0].home.x + random.randint(-2,2);
        player.y = world[0].home.y + random.randint(-2,2);
        player.z = 0;
        player.save();
    players = []
    for p in Player.objects.all():
        if(p.z > -1 and p.z == player.z and not p.uuid == player.uuid ):
            players.append({'uuid': p.uuid, 'name': p.user.username, 'x': p.x, 'y': p.y, 'z':p.z})
    #return basic info
    return { \
        'uuid': player.uuid,\
        'curpos': {'x': player.x, 'y': player.y, 'z': player.z }, \
        'players': players, \
        'map': { \
            'lvl': 1, \
            'size': { \
                'width': len(world[player.z].grid[0]), \
                'height': len(world[player.z].grid)\
            }, \
            'data': world[player.z].grid \
        } \
    }

# @csrf_exempt
@api_view(["POST"])
def move(request):
    global winner;
    dirs={"n": vector2(0,-1), "s": vector2(0,1), "e": vector2(1,0), "w": vector2(-1,0)}
    reverse_dirs = {"n": "south", "s": "north", "e": "west", "w": "east"}
    message= "";
    player = authorize_user(request.user);
    if(player==None):
        return JsonResponse({'error': 'unauthorized access', 'message': 'please login before accessing this page'},safe=True);
    player_id = player.id
    player_uuid = player.uuid
    data = json.loads(request.body)
    direction = data['direction']
    try:
        pos = vector2(player.x, player.y) + dirs[direction];
        force = False;
    except:
        pos = vector2(player.x,player.y);
    try:
        force = data['getmap']
    except:
        force = False;
    if(pos.x < 0 or pos.y < 0 or player.z < 0 or force):
        return JsonResponse(createWelcomePacket(player, True), safe=True);
    try:
        if(world[player.z].grid[pos.y][pos.x] == 0 or pos.x < 0 or pos.y < 0):
            raise;
        player.x = pos.x;
        player.y = pos.y;
        if(world[player.z].grid[pos.y][pos.x] == 'E'): #move the player to the next level and spawn them
            if(player.z+1 >= len(world)):
                #they have won the game so lets do a dance
                message = "YOU HAVE WON YAYAYAYAYAYAYAY! EVERY ONE DANCE NOW!"
                #random.seed(player.x+player.y+player.id+datetime.datetime.utcfromtimestamp(0));
                if(winner is None):
                    winner = player;
                    T = Timer(5.0, build_world);
                    T.start();
                #set up something here to tell everyone the game is over and this player has won
            else:
                player.z += 1;
                player.x = world[player.z].home.x
                player.y = world[player.z].home.y
                player.save();
                res = createWelcomePacket(player,False);
                res["message"] = "You have escaped this level, You are one step closer to getting out of this hell hole."
                print(player.z);
                return JsonResponse(res,safe=True)
        player.save();
    except:
        #message = "You can not move there!"
        pass;
    pp = []
    for p in Player.objects.all():
        if(p.z == player.z):
            pp.append(vector2(p.x,p.y))
    world[player.z].print_rooms(pp);
    players = []
    for p in Player.objects.all():
        if(p.z > -1 and p.z == player.z and not p.uuid == player.uuid):
            players.append({'uuid': p.uuid, 'name': p.user.username, 'x': p.x, 'y': p.y, 'z':p.z})
    if(not winner == None and not winner.uuid == player.uuid):
        message = player.user.username + " HAS WON YAYAYAYAYAYAYAY! EVERY ONE DANCE NOW!"
    return JsonResponse({\
        'uuid': player.uuid,\
        'curpos': {'x': player.x, 'y': player.y, 'z': player.z },\
        'players': players,\
        'message': message \
    },safe=True);

""" room = player.room()
    nextRoomID = None
    if direction == "n":
        nextRoomID = room.n_to
    elif direction == "s":
        nextRoomID = room.s_to
    elif direction == "e":
        nextRoomID = room.e_to
    elif direction == "w":
        nextRoomID = room.w_to
    if nextRoomID is not None and nextRoomID > 0:
        nextRoom = Room.objects.get(id=nextRoomID)
        player.currentRoom = nextRoomID
        player.save()
        players = nextRoom.playerNames(player_id)
        currentPlayerUUIDs = room.playerUUIDs(player_id)
        nextPlayerUUIDs = nextRoom.playerUUIDs(player_id)
        for p_uuid in currentPlayerUUIDs:
            pusher.trigger(f'p-channel-{p_uuid}', u'broadcast', {
                           'message': f'{player.user.username} has walked {dirs[direction]}.'})
        for p_uuid in nextPlayerUUIDs:
            pusher.trigger(f'p-channel-{p_uuid}', u'broadcast', {
                           'message': f'{player.user.username} has entered from the {reverse_dirs[direction]}.'})
        return JsonResponse({'name': player.user.username, 'title': nextRoom.title, 'description': nextRoom.description, 'players': players, 'error_msg': ""}, safe=True)
    else:
        players = room.playerNames(player_id)
        return JsonResponse({'name': player.user.username, 'title': room.title, 'description': room.description, 'players': players, 'error_msg': "You cannot move that way."}, safe=True) """

# pusher auth route
@csrf_exempt
@api_view(["POST"])
def pusher_auth(request):
    if not request.user.is_authenticated:
        return HttpResponseForbidden()

    pusher_client = Pusher("868770", "7163921e28b59b2fa192",
                           "d50082b134bd6f1f1cd5", "us3")

    # We must generate the token with pusher's service
    payload = pusher_client.authenticate(
        channel=request.POST['channel_name'],
        socket_id=request.POST['socket_id'])

    return JsonResponse(payload)


@csrf_exempt
@api_view(["POST"])
def say(request):
    # IMPLEMENT
    # return JsonResponse({'error':"Not yet implemented"}, safe=True, status=500)
    pusher = Pusher("868770", "7163921e28b59b2fa192",
                    "d50082b134bd6f1f1cd5", "us3")

    # collect the message from the post parameters, and save to the database
    message = Message(message=request.POST.get(
        'message', ''), status='', user=request.user)
    message.save()
    # create an dictionary from the message instance so we can send only required details to pusher
    message = {'name': message.user.username,
               'message': message.message, 'id': message.id}
    # trigger the message, channel and event to pusher
    pusher.trigger(u'a_channel', u'an_event', message)
    '''
    # authenticate the user with pusher?
    payload = pusher.authenticate(
        channel=request.POST['channel_name'],
        socket_id=request.POST['socket_id'])
    '''
    # return a json response of the broadcasted message
    return JsonResponse(message, safe=False)
