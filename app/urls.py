from django.urls import path
from rest_framework_simplejwt import views as jwt_views
from .views import home,feed,click,follow,topclicks,engageLike,engageComment,engageShare,conversation,message,notification,profile,partners,usercreate
from .views import testend

urlpatterns = [
    path('token', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('', home),
    path('feed',feed.as_view()),
    path('click',click.as_view()),
    path('follow',follow.as_view()),
    path('topclicks',topclicks.as_view()),
    path('click/<uid>/like',engageLike.as_view()),
    path('click/<uid>/comment',engageComment.as_view()),
    path('click/<uid>/share',engageShare.as_view()),
    path('conversation',conversation.as_view()),
    path('message',message.as_view()),
    path('notification',notification.as_view()),
    path('profile',profile.as_view()),
    path('partners',partners.as_view()),

    path('createuser',usercreate),

    path('testend',testend),
] 