from django.db import models
import uuid
from django.contrib.auth.hashers import  check_password
from .utils import random_color

# Create your models here.




class Board(models.Model):

    name = models.CharField(max_length=100)
    password = models.CharField(max_length=128)  
    created_at = models.DateTimeField(auto_now_add=True)
    

    def __str__(self):
        return f"{self.name} ({self.id})"
    


class Nodedata(models.Model):
    board = models.OneToOneField(Board, on_delete=models.CASCADE, related_name='data')
    content = models.JSONField()  # Stores strokes, mind map nodes, etc.


class Node(models.Model):
    
    
    x = models.FloatField(default=0)
    y = models.FloatField(default=0)
    type = models.CharField(max_length=50, default='default')
    board = models.ForeignKey(Board, related_name='nodes', on_delete=models.CASCADE)  # link to board

    label = models.CharField(max_length=255, blank=True, null=True)
    note = models.TextField(blank=True, null=True) 
    color = models.CharField(max_length=20,blank=True, null=True)
    opacity = models.FloatField(default=1.0,blank=True, null=True)

    width = models.FloatField(blank=True, null=True)
    height = models.FloatField(blank=True, null=True)

    parent = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children'
    )


    def __str__(self):
        return  self.label if self.label else f"Node {self.id}"
    

class Edge(models.Model):
    target = models.CharField(max_length=50)
    source = models.CharField(max_length= 50)
    type = models.CharField(max_length=200)
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name='edges')

    def __str__(self):
        return f"{self.source} -> {self.target} ({self.type})"
    
class ActiveBoardUser(models.Model):
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name='active_users')
    nickname = models.CharField(max_length=255)
    color = models.CharField(max_length=7, default=random_color)

    def __str__(self):
        return f"{self.nickname} in {self.board}"