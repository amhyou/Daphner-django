from django.db import models
import python_avatars as pyav
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserManager(BaseUserManager):
    
    def create_user(self, email, name, password=None):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('Users must have an email address')
        if not name:
            raise ValueError('Users must have a name')

        user = self.model(
            email=self.normalize_email(email),
            name=name,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_staffuser(self, email, name, password):
        """
        Creates and saves a staff user with the given email and password.
        """
        user = self.create_user(
            email,
            name,
            password=password,
        )
        user.staff = True
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password):
        """
        Creates and saves a superuser with the given email and password.
        """
        user = self.create_user(
            email,
            name,
            password=password,
        )
        user.staff = True
        user.admin = True
        user.save(using=self._db)
        return user

class Profile(AbstractBaseUser):

    objects = UserManager()

    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    name = models.CharField(max_length=100,blank=False,null=False)

    image = models.ImageField(upload_to='profile/')

    is_active = models.BooleanField(default=True)
    staff = models.BooleanField(default=False) # a admin user; non super-user
    admin = models.BooleanField(default=False) # a superuser

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name'] # Email & Password are required by default.

    def __str__(self):
        return(self.email + " : "+self.name)

    def get_full_name(self):
        # The user is identified by their email address
        return self.email

    def get_short_name(self):
        # The user is identified by their email address
        return self.email

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        return self.staff

    @property
    def is_admin(self):
        "Is the user a admin member?"
        return self.admin

@receiver(post_save,sender=Profile)
def generateAvatar(sender,instance,created,*args,**kwargs):
    if created:
        avatar = pyav.Avatar.random()
        avatar.render("media/profile/"+str(instance.id)+".svg")
        url = "profile/"+str(instance.id)+".svg"
        instance.image = url
        instance.save()

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
    origin = models.ForeignKey(Profile,on_delete=models.CASCADE,related_name='origin')
    msg = models.TextField()
    image = models.ImageField(upload_to="posts/")
    likes = models.IntegerField(default=0)
    comments = models.IntegerField(default=0)
    shares = models.IntegerField(default=0)
    
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