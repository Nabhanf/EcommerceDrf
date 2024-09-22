from rest_framework_simplejwt.views import TokenRefreshView
from django.urls import path
from ecommerce import views

urlpatterns = [
    path('token/',views.MyTokenObtainPairView.as_view()),
    path('token/refresh/',TokenRefreshView.as_view()),
    path('register/',views.RegisterView.as_view()),
    path('get/',views.dashboard),
    path('password_reset/',views.PasswordResetView.as_view()),
    path('password_reset_confirm/<uidb64>/<token>/', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('seller/register/', views.SellerRegisterView.as_view()),
    path('seller/login/', views.SellerTokenObtainPairView.as_view()),
    path('seller/products/', views.ProductListCreateView.as_view()),
    path('seller/products/<int:pk>/', views.ProductDetailView.as_view()),
    path('all-products/',views.ProductListView.as_view()),
    path('cart/add/',views.AddToCartView.as_view()),
    path('cart/',views.ViewCartView.as_view()),
    path('cart/update/<int:pk>/',views.UpdateCartView.as_view()),
    path('cart/remove/<int:pk>/',views.RemoveFromCartView.as_view()),
    path('razorpay/payment/', views.PurchaseView.as_view(), name='razorpay_payment'),
    path('razorpay/payment/verify/', views.RazorpayPaymentVerificationView.as_view()),
    path('test-invoice/', views.TestInvoiceView.as_view(), name='test-invoice'),
    




]
