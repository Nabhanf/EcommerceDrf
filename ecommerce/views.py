from django.conf import settings
from django.http import HttpResponse
from ecommerce.invoice import generate_invoice
from ecommerce.models import Cart, Product, Profile,User
from ecommerce.permission import IsSeller
from ecommerce.serializer import CartSerializer, ProductSerializer, SellerRegistrationSerializer, SellerTokenObtainSerializer, UserSerializer, MyTokenObtainSerializer,RegisterSerializer,PasswordResetSerializer, SetNewPasswordSerializer
from rest_framework.decorators import api_view,permission_classes
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import generics,status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from rest_framework.views import APIView
import razorpay
from django.core.mail import EmailMessage


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainSerializer

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = ([AllowAny])
    serializer_class = RegisterSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard(request):
    if request.method == "GET":
        return Response({"message":"You got a get response"})

User = get_user_model()

class PasswordResetView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = PasswordResetSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(request=request)
        return Response({"message": "Password reset email has been sent."}, status=status.HTTP_200_OK)


class PasswordResetConfirmView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = SetNewPasswordSerializer

    def patch(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and PasswordResetTokenGenerator().check_token(user, token):
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(user)
            return Response({"message": "Password has been reset successfully."}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid token or user ID."}, status=status.HTTP_400_BAD_REQUEST)

class SellerRegisterView(APIView):
    def post(self, request):
        serializer = SellerRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            seller = serializer.save()
            return Response({'message': 'Seller registered successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)        
    
class SellerTokenObtainPairView(TokenObtainPairView):
    serializer_class = SellerTokenObtainSerializer    

class ProductListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsSeller] 

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user.seller)

class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer    
    permission_classes = [IsSeller]

class ProductListView(generics.ListAPIView):
    queryset = Product.objects.all()  
    serializer_class = ProductSerializer

class AddToCartView(generics.CreateAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)   

class ViewCartView(generics.ListAPIView):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)
    
class UpdateCartView(generics.UpdateAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

class RemoveFromCartView(generics.DestroyAPIView):
    queryset = Cart.objects.all()
    permission_classes = [IsAuthenticated]

class PurchaseView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        cart_items = Cart.objects.filter(user=user)

        if not cart_items.exists():
            return Response({'message': 'Cart is empty.'}, status=status.HTTP_400_BAD_REQUEST)

        total_amount = sum(item.product.price * item.quantity for item in cart_items) * 100  

        # Create Razorpay client and order (as before)
        client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET))
        order = client.order.create({
            'amount': total_amount,
            'currency': 'INR',
            'payment_capture': 1,
        })

        
        pdf_content = generate_invoice(cart_items, total_amount, user.email)

    
        email = EmailMessage(
            'Your Invoice',
            'Thank you for your purchase. Please find your invoice attached.',
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
        )
        email.attach(pdf_content.name, pdf_content.read(), 'application/pdf')
        email.send()

        return Response({'order_id': order['id'], 'amount': total_amount}, status=status.HTTP_201_CREATED)

class RazorpayPaymentVerificationView(generics.CreateAPIView):
    def post(self, request):
        data = request.data
        payment_id = data.get('razorpay_payment_id')
        order_id = data.get('razorpay_order_id')
        signature = data.get('razorpay_signature')

        
        client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET))
        expected_signature = client.utility.generate_signature(order_id, payment_id)

        if expected_signature == signature:
            
            user = request.user
            Cart.objects.filter(user=user).delete()  
            return Response({'message': 'Payment verified and cart cleared.'}, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Payment verification failed.'}, status=status.HTTP_400_BAD_REQUEST)
        


class TestInvoiceView(APIView): #Test pdf generator
    permission_classes = [AllowAny]  

    def get(self, request):
        
        if request.user.is_authenticated:
            user_email = request.user.email
        else:
            user_email = "guest@example.com"  

        
        cart_items = [
            {"product": {"name": "Product 1", "price": 1000}, "quantity": 2},
            {"product": {"name": "Product 2", "price": 2000}, "quantity": 1},
        ]
        total_amount = sum(item['product']['price'] * item['quantity'] for item in cart_items)

        
        pdf_file = generate_invoice(cart_items, total_amount, user_email)

        
        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="invoice.pdf"'
        return response
