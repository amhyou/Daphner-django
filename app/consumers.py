import json
from urllib.parse import parse_qs
from channels.generic.websocket import AsyncWebsocketConsumer
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from jwt import decode as jwt_decode
from django.conf import settings

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        token = parse_qs(self.scope["query_string"].decode("utf8"))["token"][0]
        try:
            # This will automatically validate the token and raise an error if token is invalid
            UntypedToken(token)
        except (InvalidToken, TokenError) as e:
            # Token is invalid
            print(e)
            await self.close()
            return None
        else:
            #  Then token is valid, decode it
            decoded_data = jwt_decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        
            # Get the user using ID
            await self.accept()
            id=decoded_data["user_id"]
            print(id)
            self.identity = "user"+str(id)

            await self.channel_layer.group_add(
                self.identity,
                self.channel_name
            )

            await self.channel_layer.group_add(
                'connected_users',
                self.channel_name
            )
            await self.channel_layer.group_send(
                'connected_users',
                {
                'type':"chat_message",
                "who":self.identity,
                'what':1,
                'event':"online"
                }
            )
    

    async def receive(self, text_data):
        print(self.identity)
        event = json.loads(text_data)
        print(event)

        await self.channel_layer.group_send(
                event.get("to",""),
            {
                'type':"chat_message",
                'msg':event.get("msg"),
                'from':self.identity,
                'event':event.get("event","chat")
                
            })

    async def chat_message(self, event):
        await self.send(json.dumps(event))

    async def disconnect(self,message):
        await self.channel_layer.group_discard(
                self.identity,
                self.channel_name
            )
        await self.channel_layer.group_discard(
                "connected_users",
                self.channel_name
            )
        await self.channel_layer.group_send(
                'connected_users',
                {
                'type':"chat_message",
                "who":self.identity,
                'what':0,
                'event':"online"
                }
            )
