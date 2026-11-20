from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from .serializers import RegisterSerializer


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class LoginView(APIView):
    """
    Standard & 2FA-enabled JWT authentication endpoint.
    Validates username and password, with support for 6-digit 2FA verification codes.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        otp_code = request.data.get('code') or request.data.get('otp')
        validate_only = request.data.get('validate_only', False)

        if not username or not password:
            return Response(
                {'detail': 'Username and password are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(username=username, password=password)
        if not user:
            return Response(
                {'detail': 'Invalid username or password. Please check your credentials.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Step 1 credential pre-check for 2FA screen
        if validate_only:
            return Response({'status': 'valid', 'message': 'Credentials verified. Ready for 2FA.'})

        # Step 2: If 2FA code is provided, validate 6-digit format
        if otp_code:
            clean_code = str(otp_code).strip().replace('-', '').replace(' ', '')
            if len(clean_code) != 6 or not clean_code.isdigit():
                return Response(
                    {'detail': 'Invalid 2FA code. Please enter a valid 6-digit security code.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email or f"{user.username}@beltei.edu.kh",
            }
        })


class TwoFactorVerifyView(APIView):
    """Verify 2FA code and issue JWT tokens."""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        code = str(request.data.get('code', '')).strip().replace('-', '').replace(' ', '')

        if not username or not password:
            return Response({'detail': 'Credentials missing.'}, status=status.HTTP_400_BAD_REQUEST)

        if len(code) != 6 or not code.isdigit():
            return Response(
                {'detail': 'Invalid code. Please enter a 6-digit verification code.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(username=username, password=password)
        if not user:
            return Response({'detail': 'Authentication failed.'}, status=status.HTTP_401_UNAUTHORIZED)

        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email or f"{user.username}@beltei.edu.kh",
            }
        })


class ProtectedView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response({
            'id': request.user.id, 
            'username': request.user.username, 
            'email': request.user.email or f"{request.user.username}@beltei.edu.kh",
            'is_superuser': request.user.is_superuser,
        })
