import uuid
import os
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, \
                                       PermissionsMixin

from django.conf import settings


def recipe_image_file_path(instance, filename):
    """Generate file path for new recipe image"""
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'

    return os.path.join('uploads/recipe/', filename)


class UserManger(BaseUserManager):
    
    def create_user(self, email, password=None, **extra_fields):
        """Creates and saves new user"""
        # if the email is invalid
        if not email:
            raise ValueError('Users must have an email address')
        # extra fields used for adding more attributes in the future
        # we wont need to update the function params - only the function itself
        # normalize email function - the email input is not 
        # key sensitive (only the part after the @)
        user = self.model(email=self.normalize_email(email), **extra_fields)
        # hash the password
        user.set_password(password)
        # save the user to a certain db - basically this line is good
        # practice for a program with multiple db
        user.save(using=self._db)

        return user
    
    
    
    
    def create_superuser(self, email, password):
        """Creates and saves new super user"""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        
        return user
    
    
class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model that suppors using email instead username"""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    # create new user manager to our object
    objects = UserManger()
    
    # change the default username attribute to email (necessary only in case 
    # that the username field replaced with a different field)
    USERNAME_FIELD = 'email'
    
    
class Tag(models.Model):
    """Tag to be used for a recipe"""
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    
    def __str__(self):
        return self.name
    

class Ingredient(models.Model):
    """Ingredient to be used in a recipe"""
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    
    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Recipe object"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    title = models.CharField(max_length=255)
    time_minutes = models.IntegerField()
    price = models.DecimalField(max_digits=5, decimal_places=2)
    link = models.CharField(max_length=255, blank=True)
    ingredients = models.ManyToManyField('Ingredient')
    tags = models.ManyToManyField('Tag')
    image = models.ImageField(null=True, upload_to=recipe_image_file_path)

    def __str__(self):
        return self.title
