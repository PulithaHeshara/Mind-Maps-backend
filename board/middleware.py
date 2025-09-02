import jwt
from django.conf import settings
from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import get_user_model

User = get_user_model()

@database_sync_to_async
def get_user_from_token(token):
    try:
        access_token = AccessToken(token)
        print("Token payload:", access_token.payload)
        # Optionally fetch user model or Board here, for example:
        user = User.objects.get(id=access_token['board_name'])
        return user
      #  return access_token  # or your custom object
    except (InvalidToken, TokenError):
        return None

class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        # Extract token from query string
        query_string = scope['query_string'].decode()
        token = None
        for param in query_string.split('&'):
            if param.startswith("token="):
                token = param.split('=')[1]
                break
        
        scope['board_name'] = None 

        if token:
            try:
                access_token = AccessToken(token)
                scope['board_name'] = access_token.get('board_name')
                scope["user_id"] = access_token.get("user_id")
            except (InvalidToken, TokenError, KeyError):
                pass

        return await super().__call__(scope, receive, send)