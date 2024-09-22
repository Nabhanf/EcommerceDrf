from django.contrib import admin

from django.contrib import admin
from ecommerce.models import Product, Seller, User, Profile

class UserAdmin(admin.ModelAdmin):
    list_display = ['username','email']

class ProfileAdmin(admin.ModelAdmin):
    list_editable = ['verified',]
    list_display = ['user','full_name','verified']

admin.site.register(User,UserAdmin)
admin.site.register(Profile,ProfileAdmin)
admin.site.register(Seller)
admin.site.register(Product)