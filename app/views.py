
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

        nb = int(req.GET.get("nb","10"))

        qr = Click.objects.all()
        shuffle(qr)
        res = ClickSerializer(qr[:nb],many=True).data

        return Response(res)

class click(APIView):
    
    def post(self,req):
        id = req.user.pk

        data = json.loads(req.body)
        
        Click.objects.create(owner=id,image=data.get("img"),msg=data.get("msg"),origin=id)

        return Response({"msg":"you created a post"})

    def update(self,req):
        id = req.user.pk

        data = json.loads(req.body)

        post = Click.objects.get(pk=data.get("uid"))
        post.update(image=data.get("img"),msg=data.get("msg"))

        return Response({"msg":"you update a post"})

    def delete(self,req):
        id = req.user.pk

        data = json.loads(req.body)

        Click.objects.get(pk=data.get("uid")).delete()

        return Response({"msg":"you deleted a post"})
    

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

class partners(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self,req):
        id = req.user.pk
        me = Profile.objects.get(pk=id)

        qr = Profile.objects.exclude(Q(creator__sender=me)|Q(sender__creator=me)).exclude(pk=id)
        res = ProfileSerializer(qr,many=True).data
        print(res)
        return Response(res)

class conversation(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self,req):
        id = req.user.pk
        me = Profile.objects.get(pk=id)
        
        qr = Profile.objects.filter(Q(creator__sender=me)|Q(sender__creator=me))
        res = ProfileSerializer(qr,many=True).data

        print(res)

        return Response(res)

    def post(self,req):
        id = req.user.pk
        me = Profile.objects.get(pk=id)

        data = json.loads(req.body)
        partner = Profile.objects.get(pk=data.get("partner"))

        # check later to have unique conversation between same 2 persons
        if Conversation.objects.filter(Q(creator=partner,sender=me)|Q(creator=me,sender=partner)).exists():
            return Response({"msg":"conversation already exist , refresh to see"})
        Conversation.objects.create(creator=me,sender=partner,sender_name=partner.name)

        return Response({"msg":"conversation is created between you and your partner"})

    def delete(self,req):
        id = req.user.pk
        me = Profile.objects.get(pk=id)

        data = json.loads(req.body)
        partner = Profile.objects.get(pk=data.get("partner"))

        Conversation.objects.filter(Q(creator=me,sender=partner)|Q(creator=partner,sender=me)).delete()

        return Response({"msg":"conversation is deleted"})

class message(APIView):

    def get(self,req):
        id = req.user.pk
        me = Profile.objects.get(pk=id)

        partner = Profile.objects.get(pk=req.GET.get("partner"))

        qr = Message.objects.filter(Q(conv__creator=me,conv__sender=partner)|Q(conv__creator=partner,conv__sender=me))
        res = MessageSerializer(qr,many=True).data

        return Response(res)

    def post(self,req):
        id = req.user.pk
        me = Profile.objects.get(pk=id)

        data = json.loads(req.body)
        partner = Profile.objects.get(pk=data.get("partner"))
        try:
            conv = Conversation.objects.get(Q(creator=me,sender=partner)|Q(creator=partner,sender=me))
        except Exception as e:
            return Response({"msg":"conv not there"})
        msg = Message.objects.create(issuer=me,conv=conv,msg=data.get("msg"))
    
        return Response(MessageSerializer(msg).data)

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

class profile(APIView):
    
    def get(self,req):
        id = req.user.pk

        pr = Profile.objects.get(pk=id)
        res = ProfileSerializer(pr,many=True).data

        return Response(res)

    def post(self,req):
        id = req.user.pk

        data = json.loads(req.body)

        pr = Profile.objects.get(pk=id)

        # change something 

        return Response({"msg":"Data is changed now !"})


@api_view(["POST"])
def usercreate(req):
    data = json.loads(req.body)
    try:
        profile = Profile.objects.create_user(name=data.get("name") ,email=data.get("email"),password=data.get("password"))
        return Response({"msg":"successfully created"})
    except Exception as e:
        return Response({"msg":"error in creation : "+str(e)})

@api_view(["POST"])
def testend(req):
    data = json.loads(req.body)
    print(data)
    return Response({"tok":"dsfqsdfqdf"})