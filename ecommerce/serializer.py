from rest_framework_simplejwt.tokens import Token
from ecommerce.models import Cart, Product, User,Profile,Seller
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id','username','email']

class MyTokenObtainSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token['full_name'] = user.profile.full_name
        token['username'] = user.username
        token['email'] = user.email
        token['bio'] = user.profile.bio
        token['image'] = str(user.profile.image)
        token['verified'] = user.profile.verified

        return token
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only =True,required =True,validators=[validate_password])
    password2 = serializers.CharField(write_only =True,required =True)

    class Meta:
        model = User
        fields = ['email','username','password','password2']

    def validate(self,attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password":"Password field does not exist"})
        return attrs
            
    def create(self,validated_data):
        user = User.objects.create(username=validated_data['username'],email=validated_data['email'])
        user.set_password(validated_data['password'])
        user.save()

        return user
            
class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise ValidationError("User with this email does not exist.")
        return value

    def save(self, request):
        user = User.objects.get(email=self.validated_data['email'])
        token = PasswordResetTokenGenerator().make_token(user)
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))

    
        current_site = get_current_site(request).domain
        relative_link = reverse('password_reset_confirm', kwargs={'uidb64': uidb64, 'token': token})
        reset_url = f"http://{current_site}{relative_link}"

    
        send_mail(
            'Password Reset Request',
            f'Click the link below to reset your password:\n\n{reset_url}',
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )


class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True, min_length=8)

    def validate(self, data):
        if data['password'] != data['password2']:
            raise ValidationError("Passwords do not match.")
        return data

    def save(self, user):
        user.set_password(self.validated_data['password'])
        user.save()

class SellerRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = Seller
        fields = ['username', 'email', 'password', 'company_name']

    def create(self, validated_data):
        password = validated_data.pop('password')
        seller = Seller(**validated_data)
        seller.set_password(password)
        seller.save()
        return seller

class SellerTokenObtainSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

    
        token['username'] = user.username
        token['email'] = user.email
        token['is_seller'] = True  

        return token

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'seller', 'name', 'description', 'price', 'quantity', 'image']

class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ['id', 'user', 'product', 'quantity']