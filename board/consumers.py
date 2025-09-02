import json 

from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Board, Node, Edge, ActiveBoardUser
from .serializers import NodeSerializer,EdgeSerializer
from asgiref.sync import sync_to_async
from django.db.models import Count
from channels.exceptions import DenyConnection


import asyncio


class BoardConsumer(AsyncWebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.room_name = None
        self.room_group_name = None
        self.user_id = None

    async def connect(self):

        board_name = self.scope.get("board_name")
        if not board_name:
            raise DenyConnection("No board_name in token")
        
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"
        self.user_id = self.scope["user_id"]



        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

        self.ping_task = asyncio.create_task(self.ping_loop())

        board = await sync_to_async(Board.objects.get)(name=self.room_name)
        
        # nodes = await sync_to_async(list)(board.nodes.all())
        # nodeSerializer = NodeSerializer(nodes, many=True)
        # ndata = nodeSerializer.data

        nodes = await sync_to_async(
            lambda: list(
             board.nodes.annotate(num_children=Count('children')).order_by('-num_children')
        )
        )()

        nodeSerializer = NodeSerializer(nodes, many=True)
        ndata = nodeSerializer.data

        edges = await sync_to_async(list)(board.edges.all())
        edgeSerializer = EdgeSerializer(edges, many=True)
        edata = edgeSerializer.data
        

        await self.send(text_data=json.dumps({
            "type": "initial_data",
            "nodes": ndata,
            "edges": edata,

        }))

    @sync_to_async
    def remove_user(self,user_id):
        ActiveBoardUser.objects.filter(id=user_id).delete()

    async def disconnect(self, close_code):
        if self.room_group_name:
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        if self.user_id:
             print("remving the user")
             await self.remove_user(self.user_id)
             
    async def ping_loop(self):
        while True:
            # Send a ping frame. The client will automatically send a pong.
            await self.send(bytes_data=b'ping')

            # Wait for 30 seconds before sending the next ping
            await asyncio.sleep(30) 

    async def receive(self, text_data):

        data = json.loads(text_data)
        board = await sync_to_async(Board.objects.get)(name=self.room_name)

        if(data['type'] == "parent_add"):

            parent_data = data["parent"]
            childrensId = data["childrensId"]

            transformed_data = {
                
                "label": parent_data.get("data", {}).get("label", "Topic"),
                "x": parent_data["position"]["x"],
                "y": parent_data["position"]["y"],
                "type": parent_data.get("type", "default"),
                "board": board.id,  # Method to get board instance or ID
                "width":parent_data["style"]["width"],
                "height":parent_data["style"]["height"]
            }


            serializer = NodeSerializer(data=transformed_data)
            is_valid = await sync_to_async(serializer.is_valid)()
            if is_valid:
                await sync_to_async(serializer.save)()
                # Broadcast to group or handle success


                for childrenId in childrensId:

                    node = await sync_to_async(Node.objects.get)(id= childrenId)

                    parent_id = serializer.data["id"]
                    parent_instance = await sync_to_async(Node.objects.get)(id=parent_id)
                    node.parent = parent_instance

                    await sync_to_async(node.save)()

                print("hi")

                await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            "type": "parent.add",
                            "childrensId" :childrensId,
                            "parentId": serializer.data["id"],
                            "parent": serializer.data
                        }
                    )

            else:
                # Handle errors as needed
                print(serializer.errors)


        if data['type'] == "node_resized":
            nodeId = data["nodeId"]
            node = await sync_to_async(Node.objects.get)(id= nodeId)

            node.height = data["height"]
            node.width = data["width"]

            await sync_to_async(node.save)()

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "node.resized",
                    "nodeId": data["nodeId"],
                    "width": data["width"],
                    "height": data["height"]
                  
                }
            )

        if data["type"] == "update.color":
            nodeId = data["nodeId"]
            node = await sync_to_async(Node.objects.get)(id= nodeId)

            node.color = data["color"]
            node.opacity = data["opacity"]

            await sync_to_async(node.save)()
    
            
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "update.color",
                    "nodeId": data["nodeId"],
                    "color": data["color"],
                    "opacity": data["opacity"]
                  
                }
            )


        if data["type"] == "add_edge":

            board = await sync_to_async(Board.objects.get)(name=self.room_name)

            newEdge ={
                    "type": data["edge"]["type"],
                    "source": data["edge"]["source"],
                    "target": data["edge"]["target"],
                    "board": board.id
                }
            
            serializer = EdgeSerializer(data = newEdge)
            is_valid = await sync_to_async(serializer.is_valid)()
            user = await sync_to_async(ActiveBoardUser.objects.get)(id = data["user"]) 
            if is_valid:
                await sync_to_async(serializer.save)()
                # Broadcast to group or handle success

                await self.channel_layer.group_send(self.room_group_name,
                    {
                        "type": "add.edge",
                        "edge": serializer.data,
                         "user" : {
                                "id" : user.id,
                                "nickname":user.nickname
                        }

                    })
            else:
                # Handle errors as needed
                print(serializer.errors)



            

        if data["type"] == "update_position":

            nodeId = data["nodeId"]
            node = await sync_to_async(Node.objects.get)(id= nodeId)

            node.x = data["x"]
            node.y = data["y"]
            await sync_to_async(node.save)()
    
            
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "update.position",
                    "nodeId": data["nodeId"],
                    "x": data["x"],
                    "y": data["y"]
                }
            )

        
        if data["type"] == "update_note":

            nodeId = data["nodeId"]
            node = await sync_to_async(Node.objects.get)(id= nodeId)

            node.note = data["note"]
           
            await sync_to_async(node.save)()
    
            user = await sync_to_async(ActiveBoardUser.objects.get)(id = data["user"]) 
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "update.note",
                    "nodeId": data["nodeId"],
                    "note": data["note"],
                    "user" : {
                        "id" : user.id,
                        "cursor" : data["cursor"],
                        "nickname" : user.nickname,
                        "color" : user.color
                    }
                  
                }
            )



        if data["type"] == "node_delete":

            nodeId = data["nodeId"]
            node = await sync_to_async(Node.objects.get)(id= nodeId)
            

                # Set parent=null for children
            await sync_to_async(
                lambda: Node.objects.filter(parent=node).update(parent=None)
            )()


            await sync_to_async(node.delete)()


            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "node.delete",
                    "nodeId": data["nodeId"],               
                }
            )


        if data["type"] == "edge_delete":

            edgeId = data["edgeId"]
            edge = await sync_to_async(Edge.objects.get)(id= edgeId)
            await sync_to_async(edge.delete)()


            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "edge.delete",
                    "edgeId": data["edgeId"],               
                }
            )

        
        if data["type"] == "node_updated":

            nodeId = data["nodeId"]
            node = await sync_to_async(Node.objects.get)(id= nodeId)

            node.label = data["label"]
            await sync_to_async(node.save)()
    
            user = await sync_to_async(ActiveBoardUser.objects.get)(id = data["user"]) 
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "node.updated",
                    "nodeId": data["nodeId"],
                    "label": data["label"],
                    "user" : {
                        "id" : user.id,
                        "cursor" : data["cursor"],
                        "nickname" : user.nickname,
                        "color" : user.color
                    }
                }
            )

        if data["type"] == "node_stopTyping":
                await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "node.stopTyping",
                    "nodeId": data["nodeId"],
                    "user" : {
                        "id" : data["user"],
                    }
                }
            )
                
        if data["type"] == "note_stopTyping":
                await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "note.stopTyping",
                    "nodeId": data["nodeId"],
                    "user" : {
                        "id" : data["user"],
                    }
                }
            )


        if data["type"] == "node_add":

            node_data = data["node"]
            board = await sync_to_async(Board.objects.get)(name=self.room_name)

            user = await sync_to_async(ActiveBoardUser.objects.get)(id = data["user"]) 

            transformed_data = {
                
              # "label": node_data.get("data", {}).get("label", "Topic"),
                "x": node_data["position"]["x"],
                "y": node_data["position"]["y"],
                "type": node_data.get("type", "default"),
                "board": board.id ,  # Method to get board instance or ID

            }


            serializer = NodeSerializer(data=transformed_data)
            is_valid = await sync_to_async(serializer.is_valid)()
            if is_valid:
                await sync_to_async(serializer.save)()
                # Broadcast to group or handle success

                await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            "type": "node.add",
                            "node": serializer.data,
                             "user" : {
                                "id" : user.id,
                                "nickname":user.nickname
                            }
                        
                        }
                    )
            else:
                # Handle errors as needed
                print(serializer.errors)





        
    async def node_updated(self, event):

        await self.send(text_data=json.dumps({
            "type": "node.updated",
            "nodeId": event["nodeId"],
            "label": event["label"], 
             "user" : event["user"],

        }))

    async def node_add(self, event):

        await self.send(text_data=json.dumps({
            "type": "node.add",
            "node": event["node"],
            "user": event["user"],
            
        }))

    async def node_delete(self, event):

        await self.send(text_data=json.dumps({
            "type": "node.delete",
            "nodeId": event["nodeId"],
            
        }))

    async def edge_delete(self, event):

        await self.send(text_data=json.dumps({
            "type": "edge.delete",
            "edgeId": event["edgeId"],
            
        }))

    async def update_position(self, event):

        await self.send(text_data=json.dumps({
            "type": "update.position",
            "nodeId": event["nodeId"],
            "x": event["x"],
            "y": event["y"]
            
        }))

    async def update_note(self, event):

        await self.send(text_data=json.dumps({
            "type": "update.note",
            "nodeId": event["nodeId"],
            "note": event["note"],
            "user" : event["user"]
            
            
        }))

    async def update_color(self, event):

        await self.send(text_data=json.dumps({
            "type": "update.color",
            "nodeId": event["nodeId"],
            "color": event["color"],
            "opacity":event["opacity"]
           
            
        }))

    async def node_resized(self, event):

        await self.send(text_data=json.dumps({
            "type": "node.resize",
            "nodeId": event["nodeId"],
            "width": event["width"],
            "height":event["height"]
           
            
        }))


    async def add_edge(self, event):

        await self.send(text_data=json.dumps({
            "type": "add.edge",
            "edge": event["edge"],
            "user": event["user"]

        }))


    async def parent_add(self, event):
         
         await self.send(text_data=json.dumps({
            "type": "parent.add",
            "childrensId" : event["childrensId"],
            "parentId": event["parentId"],
            "parent": event["parent"]

        }))
         
    async def node_stopTyping(self, event):
         
         await self.send(text_data=json.dumps({
            "type": "node.stopTyping",
            "nodeId": event["nodeId"],
             "user" : event["user"],

        }))
         
    async def note_stopTyping(self, event):
         
         await self.send(text_data=json.dumps({
            "type": "note.stopTyping",
            "nodeId": event["nodeId"],
             "user" : event["user"],

        }))

