from .models import Profile,Conversation,Message,Click,Comment,Follower,Like,Share,Notification
from rest_framework.serializers import ModelSerializer

class ProfileSerializer(ModelSerializer):
    class Meta:
        model = Profile
        fields = ["id","name","image"]
        

class ConversationSerializer(ModelSerializer):
    class Meta:
        model = Conversation
        fields = "__all__"

class MessageSerializer(ModelSerializer):
    class Meta:
        model = Message
        fields = "__all__"

class LikeSerializer(ModelSerializer):
    class Meta:
        model = Like
        fields = "__all__"

class ShareSerializer(ModelSerializer):
    sender = ProfileSerializer()
    class Meta:
        model = Share
        fields = "__all__"

class CommentSerializer(ModelSerializer):
    sender = ProfileSerializer()
    class Meta:
        model = Comment
        fields = "__all__"

class ClickSerializer(ModelSerializer):
    owners = ProfileSerializer(source='owner')
    origins = ProfileSerializer(source='origin')
    likers = LikeSerializer(source="like_set",many=True)
    class Meta:
        model = Click
        fields = "__all__"
        

class FollowerSerializer(ModelSerializer):
    class Meta:
        model = Follower
        fields = "__all__"

class NotificationSerializer(ModelSerializer):
    pro = ProfileSerializer(source="who")
    class Meta:
        model = Notification
        fields = "__all__"