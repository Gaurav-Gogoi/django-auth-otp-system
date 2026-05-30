from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
import secrets


# how users are created factory
# UserManager = how users get created and managed safely 
class UserManager(BaseUserManager):  #manager helpr behavior
    def create_user(self, email, password=None):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email)
        # hashing passsword
        user.set_password(password)  #to hash the password instead of raw
        # saving in db
        user.save(using=self._db)
        return user

# this is the main user model blueprint
class User(AbstractBaseUser):  #gets auth password features
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=False)  # False until verified
    created_at = models.DateTimeField(auto_now_add=True)

    objects = UserManager()  #connecting manager to model

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

# verification state
class OTPVerification(models.Model):
    email = models.EmailField()
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False) #prevents reuse

    def __str__(self):
        return f"{self.email} - {self.otp}"


# login session tracking
class AuthToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @classmethod
    def create_token(cls, user):
        token = secrets.token_hex(32)
        return cls.objects.create(user=user, token=token)

    def __str__(self):
        return f"{self.user.email} - {self.token[:10]}..."