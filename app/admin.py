from django.contrib import admin

from .models import Profile,Conversation,Message,Click,Comment,Follower,Like,Share,Notification

admin.site.register(Profile)
admin.site.register(Conversation)
admin.site.register(Message)
admin.site.register(Click)
admin.site.register(Comment)
admin.site.register(Follower)
admin.site.register(Like)
admin.site.register(Share)
admin.site.register(Notification)