from django.utils import timezone
from datetime import datetime, timedelta
from django.conf import settings
from users.models import User, UserToken, PasswordResetToken
from .jwt_service import JWTService
from django.db import models
import secrets


class AuthService:
    """Сервис аутентификации"""

    @staticmethod
    def generate_tokens_for_user(user: User) -> dict:
        """Генерация токенов для пользователя (используется при OAuth)"""
        # Генерируем токены
        access_token = JWTService.generate_access_token(user.id)
        refresh_token = JWTService.generate_refresh_token(user.id)

        # Получаем время истечения
        access_exp = timezone.now() + timedelta(seconds=int(settings.JWT_ACCESS_EXPIRATION))
        refresh_exp = timezone.now() + timedelta(seconds=int(settings.JWT_REFRESH_EXPIRATION))

        # Сохраняем токены в БД
        JWTService.save_token(user, access_token, 'access', access_exp)
        JWTService.save_token(user, refresh_token, 'refresh', refresh_exp)

        return {
            'user': user,
            'access_token': access_token,
            'refresh_token': refresh_token
        }

    @staticmethod
    def register_user(email: str, phone: str, username: str, password: str) -> User:
        if email and User.objects.filter(email=email).exists():
            raise ValueError('Email уже зарегистрирован')
        if phone and User.objects.filter(phone=phone).exists():
            raise ValueError('Телефон уже зарегистрирован')
        if User.objects.filter(username=username).exists():
            raise ValueError('Username уже занят')

        user = User.objects.create(
            email=email,
            phone=phone,
            username=username
        )
        user.set_password(password)
        user.save()
        return user

    @staticmethod
    def login_user(identifier: str, password: str) -> dict:
        user = User.objects.filter(
            models.Q(email=identifier) | models.Q(username=identifier) | models.Q(phone=identifier),
            deleted_at__isnull=True
        ).first()

        if not user:
            raise ValueError('Неверные учетные данные')

        if not user.check_password(password):
            raise ValueError('Неверные учетные данные')

        return AuthService.generate_tokens_for_user(user)

    @staticmethod
    def refresh_tokens(refresh_token: str) -> dict:
        """Обновление пары токенов"""
        # Проверяем refresh token
        payload = JWTService.verify_refresh_token(refresh_token)
        if not payload:
            raise ValueError('Невалидный refresh токен')

        user_id = payload.get('user_id')

        # Проверяем, не отозван ли токен
        token_hash = UserToken.hash_token(refresh_token)
        stored_token = UserToken.objects.filter(
            token_hash=token_hash,
            token_type='refresh',
            is_revoked=False
        ).first()

        if not stored_token or not stored_token.is_valid():
            raise ValueError('Refresh токен отозван или истек')

        # Отзываем старый refresh token
        stored_token.is_revoked = True
        stored_token.save()

        # Получаем пользователя
        user = User.active_objects.get(id=user_id)

        return AuthService.generate_tokens_for_user(user)

    @staticmethod
    def logout_user(access_token: str, refresh_token: str = None):
        """Выход пользователя (отзыв текущих токенов)"""
        # Отзываем access token
        JWTService.revoke_token(access_token)

        # Отзываем refresh token если есть
        if refresh_token:
            JWTService.revoke_token(refresh_token)

    @staticmethod
    def logout_all_sessions(user: User):
        """Завершение всех сессий пользователя"""
        JWTService.revoke_all_user_tokens(user)

    @staticmethod
    def request_password_reset(email: str):
        user = User.active_objects.filter(email=email).first()
        if not user:
            # Не говорим, что пользователь не найден (безопасность)
            return

        reset_token = secrets.token_urlsafe(32)

        return reset_token  #

    @staticmethod
    def reset_password(token: str, new_password: str):
        pass

    @staticmethod
    def request_password_reset(email: str):
        user = User.active_objects.filter(email=email).first()
        if not user:
            return  # Не раскрываем информацию

        # Удаляем старые токены
        PasswordResetToken.objects.filter(user=user, used=False).delete()

        # Создаем новый токен
        token = secrets.token_urlsafe(32)
        expires_at = timezone.now() + timedelta(hours=1)
        PasswordResetToken.objects.create(
            user=user,
            token=token,
            expires_at=expires_at
        )
        # В реальности: отправить email с токеном. Здесь возвращаем для тестов
        return token

    @staticmethod
    def reset_password(token: str, new_password: str):
        reset_token = PasswordResetToken.objects.filter(
            token=token,
            used=False,
            expires_at__gt=timezone.now()
        ).first()

        if not reset_token:
            raise ValueError('Токен сброса недействителен или истек')

        user = reset_token.user
        user.set_password(new_password)
        user.save()

        # Отзываем все сессии
        AuthService.logout_all_sessions(user)

        # Помечаем токен как использованный
        reset_token.used = True
        reset_token.save()
