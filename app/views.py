
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

        qr = Click.objects.all().order_by('?')
        

        res = ClickSerializer(qr[:nb],many=True).data


        return Response(res)

class click(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self,req):

        rq = Click.objects.filter(owner__pk=req.GET.get("pro","0"))

        return Response(ClickSerializer(rq,many=True).data)

    def post(self,req):
        id = req.user.pk
        me = Profile.objects.get(pk=id)

        data = req.data
        
        click = Click.objects.create(owner=me,image=data.get("img"),msg=data.get("msg"),origin=me)

        return Response({"new":ClickSerializer(click).data})

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
    permission_classes = (IsAuthenticated,)
    def get(self,req):
        id = req.user.pk

        otherStats = int(req.GET.get("stats","0"))
        if otherStats:
            followers = Follower.objects.filter(pro__pk=otherStats).count()
            following = Follower.objects.filter(fan__pk=otherStats).count()
            followed = Follower.objects.filter(pro__pk=otherStats,fan__pk=id).exists()
            return Response({"followers":followers,"following":following,'followed':followed})

        me = Profile.objects.get(pk=id)

        nb = int(req.GET.get("nb","10"))
        
        qr = Profile.objects.exclude(pro__fan=me).exclude(pk=id).order_by("id")
        res = ProfileSerializer(qr,many=True).data
        
        return Response(res[:nb])

    def post(self,req):
        id = req.user.pk
        me = Profile.objects.get(pk=id)

        data = json.loads(req.body)
        star_id = data.get("star_id")
        star = Profile.objects.get(pk=star_id)

        if not Follower.objects.filter(pro=star,fan=me).exists():
            Follower.objects.create(pro=star,fan=me)
            Notification.objects.create(to=star,who=me,msg=f"user{id} followed you")
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
    permission_classes = (IsAuthenticated,)
    def get(self,req):
        id = req.user.pk
        nb = int(req.GET.get("nb","20"))

        qr = Click.objects.all()
        res = ClickSerializer(qr,many=True).data
        res.sort(key=lambda x:x["likes"]+2*x["comments"]+3*x["shares"],reverse=True)

        return Response(res[:nb])

class engageLike(APIView):
    permission_classes = (IsAuthenticated,)
    def post(self,req,uid):
        id = req.user.pk
        me = Profile.objects.get(pk=id)
        post = Click.objects.get(pk=uid)

        if Like.objects.filter(click=post,sender=me).exists():
            Like.objects.filter(click=post,sender=me).delete()
            post.likes -= 1
            post.save()
            return Response({"diff":-1})
        else:
            Like.objects.create(click=post,sender=me)
            post.likes += 1
            post.save()
            Notification.objects.create(to=post.owner,who=me,msg=f"{me.id} liked your post {post.id}")
            return Response({"diff":1})

class engageComment(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self,req,uid):
        id = req.user.pk
        post = Click.objects.get(pk=uid)
        commenters = Comment.objects.filter(click=post).order_by('time')
        return Response(CommentSerializer(commenters[::-1],many=True).data)

    def post(self,req,uid):
        id = req.user.pk
        me = Profile.objects.get(pk=id)
        post = Click.objects.get(pk=uid)
        data = json.loads(req.body)
        newcom = Comment.objects.create(click=post,sender=me,msg=data.get("msg"))
        post.comments +=1
        post.save()
        Notification.objects.create(to=post.owner,who=me,msg=f"{me.id} commented your post {post.id}")
        return Response({"new":CommentSerializer(newcom).data})

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
    permission_classes = (IsAuthenticated,)
    def get(self,req,uid):
        id = req.user.pk
        post = Click.objects.get(pk=uid)
        sharers = Share.objects.filter(click=post).order_by('time')
        return Response(ShareSerializer(sharers[::-1],many=True).data)

    def post(self,req,uid):
        id = req.user.pk
        me = Profile.objects.get(pk=id)
        post = Click.objects.get(pk=uid)
        data = json.loads(req.body)
        newshare = Share.objects.create(click=post,sender=me)
        post.shares += 1
        post.save()
        Click.objects.create(owner=me,image=post.image,msg=post.msg,origin=post.owner)
        Notification.objects.create(to=post.owner,who=me,msg=f"{me.id} shared your post {post.id}")
        return Response({"new":ShareSerializer(newshare).data})

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
    permission_classes = (IsAuthenticated,)
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
    permission_classes = (IsAuthenticated,)
    def get(self,req):
        id = req.user.pk

        qr = Notification.objects.filter(to=id).order_by("time")
        res = NotificationSerializer(qr,many=True).data

        return Response(res[::-1])

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
    permission_classes = (IsAuthenticated,)
    def get(self,req):
        id = req.user.pk

        otherUser = int(req.GET.get("stats","0"))
        if otherUser:
            pr = Profile.objects.get(pk=otherUser)
            return Response(ProfileSerializer(pr).data)

        pr = Profile.objects.get(pk=id)
        res = ProfileSerializer(pr).data

        return Response(res)

    def post(self,req):
        id = req.user.pk
        pr = Profile.objects.get(pk=id)
        try:
            data = json.loads(req.body)
            if data.get("type")=="smya":
                pr.name = data.get("value")
                pr.save()
        except Exception as e:
            print(req.data)
            pr.image = req.data.get("image")
            pr.save()
            return Response({"url":pr.image.url})

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