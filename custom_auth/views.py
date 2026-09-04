from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import redirect
from django.http import JsonResponse
from django.conf import settings
from .auth_service import AuthService
from .oauth_service import OAuthService
from .serializers import RegisterSerializer, LoginSerializer, UserResponseSerializer, ForgotPasswordSerializer, \
    ResetPasswordSerializer
from .permissions import CookieAuthentication


class RegisterView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = AuthService.register_user(
                email=serializer.validated_data.get('email'),
                phone=serializer.validated_data.get('phone'),
                username=serializer.validated_data['username'],
                password=serializer.validated_data['password']
            )
            response_data = UserResponseSerializer(user).data
            return Response(response_data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    """Вход пользователя"""
    permission_classes = []

    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            result = AuthService.login_user(
                identifier=serializer.validated_data['identifier'],
                password=serializer.validated_data['password']
            )

            response = Response({
                'user': UserResponseSerializer(result['user']).data
            }, status=status.HTTP_200_OK)

            # Устанавливаем cookies
            response.set_cookie(
                'access_token',
                result['access_token'],
                httponly=True,
                secure=not settings.DEBUG,
                samesite='Lax',
                max_age=settings.JWT_ACCESS_EXPIRATION
            )
            response.set_cookie(
                'refresh_token',
                result['refresh_token'],
                httponly=True,
                secure=not settings.DEBUG,
                samesite='Lax',
                max_age=settings.JWT_REFRESH_EXPIRATION
            )

            return response

        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_401_UNAUTHORIZED)


class RefreshTokenView(APIView):
    """Обновление токенов"""
    permission_classes = []

    def post(self, request):
        refresh_token = request.COOKIES.get('refresh_token')

        if not refresh_token:
            return Response({'error': 'Refresh token не найден'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            result = AuthService.refresh_tokens(refresh_token)

            response = Response({
                'user': UserResponseSerializer(result['user']).data
            }, status=status.HTTP_200_OK)

            # Обновляем cookies
            response.set_cookie(
                'access_token',
                result['access_token'],
                httponly=True,
                secure=not settings.DEBUG,
                samesite='Lax',
                max_age=settings.JWT_ACCESS_EXPIRATION
            )
            response.set_cookie(
                'refresh_token',
                result['refresh_token'],
                httponly=True,
                secure=not settings.DEBUG,
                samesite='Lax',
                max_age=settings.JWT_REFRESH_EXPIRATION
            )

            return response

        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_401_UNAUTHORIZED)


class WhoAmIView(APIView):
    """Получение информации о текущем пользователе"""

    def get(self, request):
        if not getattr(request.user, 'is_authenticated', False):
            return Response({'error': 'Не авторизован'}, status=status.HTTP_401_UNAUTHORIZED)

        return Response(UserResponseSerializer(request.user).data)


class LogoutView(APIView):
    """Выход из текущей сессии"""

    def post(self, request):
        access_token = request.COOKIES.get('access_token')
        refresh_token = request.COOKIES.get('refresh_token')

        if not getattr(request.user, 'is_authenticated', False):
            return Response({'error': 'Не авторизован'}, status=status.HTTP_401_UNAUTHORIZED)

        if access_token:
            AuthService.logout_user(access_token, refresh_token)

        response = Response({'message': 'Выход выполнен'}, status=status.HTTP_200_OK)

        # Удаляем cookies
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')

        return response


class LogoutAllView(APIView):
    """Выход из всех сессий"""

    def post(self, request):
        if not getattr(request.user, 'is_authenticated', False):
            return Response({'error': 'Не авторизован'}, status=status.HTTP_401_UNAUTHORIZED)

        AuthService.logout_all_sessions(request.user)

        response = Response({'message': 'Все сессии завершены'}, status=status.HTTP_200_OK)
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')

        return response


class OAuthYandexView(APIView):
    """Инициация OAuth через Yandex"""
    permission_classes = []

    def get(self, request):
        auth_url, state = OAuthService.get_yandex_auth_url()

        # Сохраняем state в сессии для проверки при callback
        request.session['oauth_state'] = state

        return redirect(auth_url)


class OAuthYandexCallbackView(APIView):
    """Callback для OAuth Yandex"""
    permission_classes = []

    def get(self, request):
        code = request.GET.get('code')
        state = request.GET.get('state')
        error = request.GET.get('error')

        # Проверяем на ошибку
        if error:
            return JsonResponse({'error': f'Ошибка OAuth: {error}'}, status=400)

        if not code:
            return JsonResponse({'error': 'Код авторизации не получен'}, status=400)

        # Проверяем state (защита от CSRF)
        saved_state = request.session.get('oauth_state')
        if not saved_state or saved_state != state:
            return JsonResponse({'error': 'Неверный state параметр (возможная CSRF атака)'}, status=400)

        # Очищаем state из сессии
        request.session.pop('oauth_state', None)

        try:
            result = OAuthService.handle_yandex_oauth(code)

            # Перенаправляем на фронтенд с установкой cookies
            response = redirect('http://localhost:4200')
            response.set_cookie(
                'access_token',
                result['access_token'],
                httponly=True,
                secure=not settings.DEBUG,
                samesite='Lax',
                max_age=settings.JWT_ACCESS_EXPIRATION
            )
            response.set_cookie(
                'refresh_token',
                result['refresh_token'],
                httponly=True,
                secure=not settings.DEBUG,
                samesite='Lax',
                max_age=settings.JWT_REFRESH_EXPIRATION
            )

            return response

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)


class ForgotPasswordView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data['email']
        AuthService.request_password_reset(email)

        # Всегда возвращаем успех (даже если email нет в БД)
        return Response({'message': 'Если email существует, на него отправлена инструкция'},
                        status=status.HTTP_200_OK)


class ResetPasswordView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            AuthService.reset_password(
                token=serializer.validated_data['token'],
                new_password=serializer.validated_data['new_password']
            )
            return Response({'message': 'Пароль успешно сброшен'}, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
