from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import User, OTPVerification, AuthToken
from .serializers import (
    RegisterSerializer,
    VerifyOTPSerializer,
    LoginSerializer,
    UserSerializer
)
from .utils import generate_otp, send_otp_email


class RegisterView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email', 'password'],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING),
                'password': openapi.Schema(type=openapi.TYPE_STRING),
            }
        )
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        # extracts validated data from the serializer
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        
        user, created = User.objects.get_or_create(email=email)
        
        if created or not user.is_active:
            user.set_password(password)
            user.is_active = False
        # user cannot login isactive is false
            user.save()
        otp = generate_otp()
        
        OTPVerification.objects.create(email=email, otp=otp)
        # store otp
        send_otp_email(email, otp)
        # user receives the code
        return Response({'message': 'OTP sent to your email. Please verify.'}, status=201)


class VerifyOTPView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email', 'otp'],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING),
                'otp': openapi.Schema(type=openapi.TYPE_STRING),
            }
        )
    )
    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        
        email = serializer.validated_data['email']
        otp = serializer.validated_data['otp']
        
        time_limit = timezone.now() - timedelta(minutes=10) #otp expiry
        # system checks all macthing valid email otp unsued otp not expired
        otp_obj = OTPVerification.objects.filter(
            email=email,
            otp=otp,
            is_used=False,
            # prevents otp reuse
            created_at__gte=time_limit
        ).last()
        
        if not otp_obj:
            return Response({'error': 'Invalid or expired OTP.'}, status=400)
        try:
            user = User.objects.get(email=email)
            user.is_active = True
            user.save()
            otp_obj.is_used = True
            otp_obj.save()
        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=404)
        return Response({'message': 'Email verified successfully.'})


class LoginView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email', 'password'],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING),
                'password': openapi.Schema(type=openapi.TYPE_STRING),
            }
        )
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        
        user = authenticate(request, username=email, password=password)
        if not user:
            return Response({'error': 'Invalid credentials.'}, status=401)
        if not user.is_active:
            return Response({'error': 'Account not verified.'}, status=403)
        
        auth_token = AuthToken.create_token(user)
        # creates random secure token
        
        response = Response({'message': 'Login successful.'})
        # store db then send to browser
        # store token in browser for login domain
        response.set_cookie(
            key='auth_token',
            value=auth_token.token,
            httponly=True,
            secure=getattr(settings, 'AUTH_COOKIE_SECURE', False),
            samesite='Lax',
        )
        return response


# access protected route/me
class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        token = request.COOKIES.get('auth_token')
        if token:
            AuthToken.objects.filter(token=token).delete()
        response = Response({'message': 'Logged out successfully.'})
        response.delete_cookie('auth_token')
        return response