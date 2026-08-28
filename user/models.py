from django.db import models
from .custom_manager import CustomUserManager

from django.contrib.auth.models import AbstractUser 
from django.utils.translation import gettext_lazy as _ 

from utils import user_roles



class User(AbstractUser):

    username = None 


    roles = models.CharField(
        max_length=15,
        choices=user_roles,
        default='Customer'
    )
    email = models.EmailField(unique=True,db_index=True)
    # phone number may be null
    phone_number = models.CharField(max_length= 20,null=True,blank=True,db_index=True) 

    # profile_image may be also be  null
    profile_image = models.ImageField(upload_to='images/',null=True,blank=True)


    objects = CustomUserManager() 
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []


    def __str__(self):
        return f'{self.email}'


