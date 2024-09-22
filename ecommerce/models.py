from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser,Group, Permission
from django.db.models.signals import post_save

class User(AbstractUser):
    username = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.username

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=300)
    bio = models.CharField(max_length=300)
    image = models.ImageField(default="default.jpg", upload_to="user_images")
    verified = models.BooleanField(default=False)

    def __str__(self):
        return self.full_name
    
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

def save_user_profile(sender,instance,**kwargs):
    instance.profile.save()    

post_save.connect(create_user_profile, sender=User)
post_save.connect(save_user_profile,sender=User)

class Seller(User):  
    company_name = models.CharField(max_length=255)

    class Meta:
        verbose_name = 'Seller'
        verbose_name_plural = 'Sellers'

    def __str__(self):
        return self.company_name

from django.db import models

class Product(models.Model):
    seller = models.ForeignKey('Seller', on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField() 
    image = models.ImageField(upload_to='products/', blank=True, null=True)  

    def __str__(self):
        return self.name

class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    
    class Meta:
        unique_together = ('user', 'product')
