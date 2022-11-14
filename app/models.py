from django.db import models

class Profile(models.Model):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100)
    image = models.ImageField()
    joined = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return(self.email + " : "+self.name)


class Conversation(models.Model):
    creator = models.ForeignKey(Profile,on_delete=models.CASCADE,related_name='creator')
    sender = models.ForeignKey(Profile,on_delete=models.CASCADE,related_name='sender')
    not_seen = models.IntegerField(default=0)
    sender_name = models.CharField(max_length=100)

    def __str__(self):
        return(self.sender)

class Message(models.Model):
    issuer = models.ForeignKey(Profile,on_delete=models.CASCADE)
    conv = models.ForeignKey(Conversation,on_delete=models.CASCADE)
    msg = models.TextField()
    vu = models.BooleanField(default=False)
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return(self.msg[:10]+"...")


class Click(models.Model):
    owner = models.ForeignKey(Profile,on_delete=models.CASCADE,related_name='owner')
    image = models.ImageField()
    msg = models.TextField()
    likes = models.IntegerField(default=0)
    comments = models.IntegerField(default=0)
    shares = models.IntegerField(default=0)
    origin = models.ForeignKey(Profile,on_delete=models.CASCADE,related_name='origin')
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return(self.owner.name +" : "+ self.msg[:10])


class Comment(models.Model):
    click = models.ForeignKey(Click,on_delete=models.CASCADE)
    sender = models.ForeignKey(Profile,on_delete=models.CASCADE)
    msg = models.TextField()
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return("comment by "+ self.sender)

class Like(models.Model):
    click = models.ForeignKey(Click,on_delete=models.CASCADE)
    sender = models.ForeignKey(Profile,on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return("liked by "+self.sender)

class Share(models.Model):
    click = models.ForeignKey(Click,on_delete=models.CASCADE)
    sender = models.ForeignKey(Profile,on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return("shared by "+self.sender)


class Follower(models.Model):
    pro = models.ForeignKey(Profile,on_delete=models.CASCADE,related_name="pro")
    fan = models.ForeignKey(Profile,on_delete=models.CASCADE,related_name="fan")
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return(self.fan + " is fan of " + self.pro)



class Notification(models.Model):
    to = models.ForeignKey(Profile,on_delete=models.CASCADE,related_name='to')
    who = models.ForeignKey(Profile,on_delete=models.CASCADE,related_name='who')
    msg = models.CharField(max_length=200)

    def __str__(self):
        return("notif from "+self.who+" to "+self.to)