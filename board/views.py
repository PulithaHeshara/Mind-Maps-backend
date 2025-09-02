from django.shortcuts import render
from .serializers import (
    BoardLoginSerializer,
    BoardCreateSerializer,
    ActiveBoardUserSerializer
)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Board

from .models import ActiveBoardUser


# Create your views here.


class BoardCreateView(APIView):

    def post(self, request):
        serializer = BoardCreateSerializer(data=request.data)
        if serializer.is_valid():
            board = serializer.save()
            return Response({'room_code': board.id}, status=201)
        return Response({"error": serializer.errors}, status=400)
    
class BoardLoginView(APIView):

    def post(self, request):
        serializer = BoardLoginSerializer(data=request.data["login_data"])
        print(request.data)
        if serializer.is_valid():
            
            refresh = RefreshToken()
            refresh['board_name'] = serializer.validated_data["name"]
            
            
            board = Board.objects.get(name = serializer.validated_data["name"] )

            active_user_serializer = ActiveBoardUserSerializer(data={
                "board": board.id,
                "nickname": request.data.get("nickname")
            })

            if active_user_serializer.is_valid():
                active_user = active_user_serializer.save()
            else:
                return Response(active_user_serializer.errors, status=400)
            
            refresh["user_id"] = active_user.id

            return Response({
                        'access': str(refresh.access_token),
                        'refresh': str(refresh),
                        'board_name': serializer.validated_data["name"],
                        "board_id": board.id,
                        "user_id": active_user.id
                    })

        return Response({'detail': 'Invalid room code or password'}, status=401)
    
