from rest_framework import serializers
from .models import Board, Node, Edge, ActiveBoardUser
from django.contrib.auth.hashers import make_password,check_password
from .utils import generate_unique_nickname


class BoardLoginSerializer(serializers.ModelSerializer):

    class Meta:
        model = Board
        fields = ['name', 'password']

    def validate(self, data):
        name = data["name"] 
        password = data["password"]

        try:
            board = Board.objects.get(name = name)

        except Board.DoesNotExist:
            raise serializers.ValidationError("Board not found")
        if not check_password(password, board.password):
            raise serializers.ValidationError("Incorrect password")
        
        return {
            "name": board.name,
            "password": board.password
        }


class BoardCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Board
        fields = ['name', 'password']

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)
    
    def validate_name(self, name):
        if Board.objects.filter(name=name).exists():
            raise serializers.ValidationError("This board name is already taken.")
        return name


class NodeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Node
        fields = [ "id","label", "x", "y", "type","board","note","color","opacity","width","height","parent"]

class EdgeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Edge
        fields = [ "id", "source", "target", "type","board"]
    
class ActiveBoardUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = ActiveBoardUser
        fields = [ "id", "board", "nickname"]

    def validate(self, data):
        board = data["board"]
        

        unique_name = generate_unique_nickname(board, data["nickname"])
        data["nickname"] = unique_name
        return data
