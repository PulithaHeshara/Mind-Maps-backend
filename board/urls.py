
from django.urls import path
from .views import (
    BoardCreateView,
    BoardLoginView
)
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [

    path('login', BoardLoginView.as_view()),
    path('create', BoardCreateView.as_view()),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]