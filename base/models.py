from django.db import models

# Create your models here.
from django.contrib.auth.models import User

# "TOPIC" IS MAIN PARENT
class Topic(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


# "ROOM" IS CHILD OF "TOPIC"
class Room(models.Model):
    host = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)   # if 'User' gets deleted, don't delete 'Room'
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True)  # if 'Topic' gets deleted, don't delete 'Room'
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    participants = models.ManyToManyField(User, related_name='participants', blank=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-updated', '-created'] # LATEST ITEM IS ON TOP OF LIST

    # CREATE A STRING REPRESENTATION OF THIS ROOM
    def __str__(self):
        return self.name


# "MESSAGE" IS CHILD OF "USER" & "ROOM"
class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)    # if 'User' gets deleted all the children get deleted
    room = models.ForeignKey(Room, on_delete=models.CASCADE)    # if 'room' gets deleted all the children get deleted
    body = models.TextField()
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-updated', '-created'] # LATEST ITEM IS ON TOP OF LIST

    def __str__(self):
        return self.body[0:50]
