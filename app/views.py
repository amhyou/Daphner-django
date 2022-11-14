
from rest_framework.response import Response
from rest_framework.decorators import api_view,APIView
from rest_framework.permissions import IsAuthenticated
from .models import Profile,Conversation,Message,Click,Comment,Follower,Like,Share,Notification
from .serializers import ProfileSerializer,ConversationSerializer,MessageSerializer,ClickSerializer,CommentSerializer,FollowerSerializer,LikeSerializer,ShareSerializer,NotificationSerializer

from random import shuffle
import json

@api_view(['GET'])
def home(req):
    return Response({"greeting":"hello world"})


class feed(APIView):

    permission_classes = (IsAuthenticated,)

    def get(self,req):
        id = req.user.pk

        qr = Click.objects.all()
        shuffle(qr)
        res = ClickSerializer(qr,many=True).data

        return Response(res)

class click(APIView):
    
    def post(self,req):
        data = json.loads(req.body)
        id = data.get("id")

        return Response({"success":True})

class follow(APIView):

    def get(self,req):
        id = req.user.pk

        nb = req.GET.get("nb")
        
        qr = Profile.objects.all()
        shuffle(qr)
        res = ProfileSerializer(qr[:nb],many=True).data

        return Response(res)

    def post(self,req):
        id = req.user.pk

        data = json.loads(req.body)
        star_id = data.get("star_id")

        if not Follower.objects.filter(pro=star_id,fan=id).exists():
            Follower.objects.create(pro=star_id,fan=id)
            return Response({"subscribed":"success"})
        return Response({"subscribed":"echec, perhaps it's already subscribed to!"})

    def delete(self,req):
        id = req.user.pk

        data = json.loads(req.body)
        star_id = data.get("star_id")

        if Follower.objects.filter(pro=star_id,fan=id).exists():
            Follower.objects.filter(pro=star_id,fan=id).delete()
            return Response({"unsubscrie":"success"})
        return Response({"unsubscrie":"echec, perhaps not subscribed to yet!"})

class topclicks(APIView):
    def get(self,req):
        id = req.user.pk

        nb = req.GET.get("nb")

        qr = Click.objects.all()
        qr.sort(key=lambda x:x.likes+2*x.comments+3*x.shares)
        resp = ClickSerializer(qr[:nb],many=True).data

        return Response(qr)

class engageLike(APIView):

    def post(self,req,uid):
        id = req.user.pk
        post = Click.objects.get(pk=uid)

        if Like.objects.filter(click=post,sender=id).exists():
            Like.objects.filter(click=post,sender=id).delete()
            post.likes += 1
            post.save()
            return Response({"msg":"you unliked the post"})
        else:
            Like.objects.create(click=post,sender=id)
            post.likes -= 1
            post.save()
            return Response({"msg":"you liked the post"})

class engageComment(APIView):

    def post(self,req,uid):
        id = req.user.pk
        data = json.loads(req.body)
        Comment.objects.create(click=uid,sender=id,msg=data.get("msg"))
        return Response({"msg":"comment added to the post"})

    def update(self,req,uid):
        id = req.user.pk
        data = json.loads(req.body)
        Comment.objects.filter(pk=data.get("uid")).update(msg=data.get("msg"))
        return Response({"msg":"comment updated"})

    def delete(self,req,uid):
        id = req.user.pk
        data = json.loads(req.body)
        Comment.objects.filter(pk=data.get("uid")).delete()
        return Response({"msg":"comment deleted from te post"})

class engageShare(APIView):

    def post(self,req,uid):
        id = req.user.pk
        post = Click.objects.get(pk=id)
        data = json.loads(req.body)
        Share.objects.create(click=uid,sender=id)
        post.shares += 1
        post.save()
        Click.objects.create(owner=id,image=post.image,msg=post.msg,origin=post.owner)
        return Response({"msg":"this post is added to your profile"})

from django.db.models import Q

class conversation(APIView):
    def get(self,req):
        id = req.user.pk

        qr = Conversation.objects.filter(Q(creator=id)|Q(sender=id))
        res = ConversationSerializer(qr,many=True).data

        return Response(res)

    def post(self,req):
        id = req.user.pk

        data = json.loads(req.body)
        partner = data.get("partner")
        partner_name = Profile.objects.get(pk=partner).name

        # check later to have unique conversation between same 2 persons
        Conversation.objects.create(creator=id,sender=partner,sender_name=partner_name)

        return Response({"msg":"conversation is created between you and your partner"})

    def delete(self,req):
        id = req.user.pk

        data = json.loads(req.body)
        partner = data.get("partner")

        Conversation.objects.filter(Q(creator=id,sender=partner)|Q(creator=partner,sender=id)).delete()

        return Response({"msg":"conversation is created between you and your partner"})

class message(APIView):

    def get(self,req,uid):
        id = req.user.pk

        qr = Message.objects.filter(conv=uid)
        res = MessageSerializer(qr,many=True).data

        return Response(res)

    def post(self,req,uid):
        id = req.user.pk

        data = json.loads(req.body)
        msg = data.get("msg")

        Message.objects.create(issuer=id,conv=uid,msg=msg)

        return Response({"msg":"message is created in the conversation"})

    def delete(self,req,uid):
        id = req.user.pk

        data = json.loads(req.body)
        msg_id = data.get("uid")

        Message.objects.filter(pk=msg_id).delete()

        return Response({"msg":"message is created in the conversation"})

class notification(APIView):

    def get(self,req):
        id = req.user.pk

        qr = Notification.objects.filter(to=id)
        res = NotificationSerializer(qr,many=True).data

        return Response(res)

    def post(self,req):
        id = req.user.pk

        data = json.loads(req.body)
        who = data.get("uid")
        event = data.get("event")

        match event:
            case "like":
                msg = "someone liked your post"
            case "comment":
                msg = "someone commented your post"
            case "share":
                msg = "someone shared your post"
            case "follow":
                msg = "someone followed you"
            case _:
                msg = ""


        Notification.objects.create(to=id,who=who,msg=msg)

        return Response({"msg":"notification is created"})
