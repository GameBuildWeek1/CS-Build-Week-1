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
from util.sample_generator import World
import random
# instantiate pusher
# pusher = Pusher(app_id=config('PUSHER_APP_ID'), key=config('PUSHER_KEY'), secret=config('PUSHER_SECRET'), cluster=config('PUSHER_CLUSTER'))
world = []
for i in range(4):
    w = World()
    num_rooms = 1000
    width = int(2**(5+(i*0.5)))
    height = int(2**(4+(i*0.5)))
    w.generate_rooms(width, height, num_rooms, random.randint(
        width//4, (3*width)//4), random.randint(height//4, (3*height)//4))
    w.print_rooms()
    world.append(w.grid)


@csrf_exempt
@api_view(["GET"])
def initialize(request):
    user = request.user
    player = user.player
    player_id = player.id
    uuid = player.uuid
    room = player.room()
    players = room.playerNames(player_id)
    return JsonResponse({'uuid': uuid, 'name': player.user.username, 'title': room.title, 'description': room.description, 'players': players}, safe=True)


# @csrf_exempt
@api_view(["POST"])
def move(request):
    dirs = {"n": "north", "s": "south", "e": "east", "w": "west"}
    reverse_dirs = {"n": "south", "s": "north", "e": "west", "w": "east"}
    player = request.user.player
    player_id = player.id
    player_uuid = player.uuid
    data = json.loads(request.body)
    direction = data['direction']
    room = player.room()
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
        return JsonResponse({'name': player.user.username, 'title': room.title, 'description': room.description, 'players': players, 'error_msg': "You cannot move that way."}, safe=True)

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
