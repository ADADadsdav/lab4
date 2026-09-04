import jwt
import hashlib
import secrets
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone
from users.models import User, UserToken


class JWTService:
    """Сервис для работы с JWT токенами"""

    @staticmethod
    def generate_access_token(user_id: int) -> str:
        """Генерация Access Token"""
        payload = {
            'user_id': user_id,
            'type': 'access',
            'exp': timezone.now() + timedelta(seconds=int(settings.JWT_ACCESS_EXPIRATION)),
            'iat': timezone.now(),
            'jti': secrets.token_urlsafe(16)
        }

        token = jwt.encode(
            payload,
            settings.JWT_ACCESS_SECRET,
            algorithm='HS256'
        )

        return token

    @staticmethod
    def generate_refresh_token(user_id: int) -> str:
        """Генерация Refresh Token"""
        payload = {
            'user_id': user_id,
            'type': 'refresh',
            'exp': timezone.now() + timedelta(seconds=int(settings.JWT_REFRESH_EXPIRATION)),
            'iat': timezone.now(),
            'jti': secrets.token_urlsafe(16)
        }

        token = jwt.encode(
            payload,
            settings.JWT_REFRESH_SECRET,
            algorithm='HS256'
        )

        return token

    @staticmethod
    def verify_access_token(token: str) -> dict:
        """Проверка Access Token"""
        try:
            payload = jwt.decode(
                token,
                settings.JWT_ACCESS_SECRET,
                algorithms=['HS256']
            )

            if payload.get('type') != 'access':
                return None

            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    @staticmethod
    def verify_refresh_token(token: str) -> dict:
        """Проверка Refresh Token"""
        try:
            payload = jwt.decode(
                token,
                settings.JWT_REFRESH_SECRET,
                algorithms=['HS256']
            )

            if payload.get('type') != 'refresh':
                return None

            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    @staticmethod
    def save_token(user: User, token: str, token_type: str, expires_at: datetime):
        """Сохранение токена в БД (в хешированном виде)"""
        token_hash = UserToken.hash_token(token)

        UserToken.objects.create(
            user=user,
            token_hash=token_hash,
            token_type=token_type,
            expires_at=expires_at
        )

    @staticmethod
    def revoke_token(token: str):
        """Отзыв токена"""
        token_hash = UserToken.hash_token(token)

        # Пытаемся найти и отозвать токен
        user_token = UserToken.objects.filter(
            token_hash=token_hash,
            is_revoked=False
        ).first()

        if user_token:
            user_token.is_revoked = True
            user_token.save()

    @staticmethod
    def revoke_all_user_tokens(user: User):
        """Отзыв всех токенов пользователя"""
        UserToken.objects.filter(
            user=user,
            is_revoked=False
        ).update(is_revoked=True)
