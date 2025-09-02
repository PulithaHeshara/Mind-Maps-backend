from django.contrib import admin
from .models import Board
from .models import Node
from .models import Edge
from .models import ActiveBoardUser

# Register your models here.

admin.site.register(Board)
admin.site.register(Node)
#admin.site.register(Edge)
admin.site.register(ActiveBoardUser)