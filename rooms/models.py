from django.conf import settings
from django.db import models

# Create your models here.
class Topic(models.Model):
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title


class Room(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True)
    host = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='participants', blank=True)
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=1000, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created', '-updated']

    def __str__(self):
        return self.title


class Message(models.Model):
    chatroom = models.ForeignKey(Room, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, models.SET_NULL, null=True)
    content = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content