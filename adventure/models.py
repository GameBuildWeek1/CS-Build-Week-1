from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
import uuid

class Room(models.Model):
    homex = models.IntegerField(default=0)
    homey = models.IntegerField(default=0)
    grid = models.TextField(default="");

class Player(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    x = models.IntegerField(default=-1)
    y = models.IntegerField(default=-1)
    z = models.IntegerField(default=-1)
    w = models.IntegerField(default= 0);
    last_update = models.IntegerField(default=0)
    def initialize(self):
        pass;
    def room(self):
        try:
            return Room.objects.get(id=self.currentRoom)
        except Room.DoesNotExist:
            self.initialize()
            return self.room()

@receiver(post_save, sender=User)
def create_user_player(sender, instance, created, **kwargs):
    if created:
        Player.objects.create(user=instance)
        Token.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_player(sender, instance, **kwargs):
    instance.player.save()



class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.CharField(max_length=500, blank=True, null=True)
    create_at = models.IntegerField(default=0)

    def __str__(self):
        return str(self.message)

