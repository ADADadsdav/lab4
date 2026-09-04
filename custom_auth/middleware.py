from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from .jwt_service import JWTService
from users.models import User, UserToken


class AuthenticationMiddleware(MiddlewareMixin):
    """Middleware для аутентификации через JWT в cookies"""

    def process_request(self, request):
        """Извлечение и проверка access токена из cookies"""
        # Пропускаем публичные эндпоинты
        public_paths = [
            '/auth/register', '/auth/login', '/auth/refresh',
            '/auth/oauth/', '/auth/forgot-password', '/auth/reset-password'
        ]

        if any(request.path.startswith(path) for path in public_paths):
            return None

        # Получаем токен из cookies
        access_token = request.COOKIES.get('access_token')

        if not access_token:
            return None

        # Проверяем токен
        payload = JWTService.verify_access_token(access_token)

        if not payload:
            return None

        # Проверяем, что токен не был отозван (logout должен немедленно
        # прекращать доступ, а не только ждать истечения JWT).
        token_hash = UserToken.hash_token(access_token)
        stored_token = UserToken.objects.filter(
            token_hash=token_hash, token_type='access', is_revoked=False
        ).first()
        if not stored_token or not stored_token.is_valid():
            request.user = None
            request.user_id = None
            return None

        # Получаем пользователя
        try:
            user = User.objects.get(id=payload['user_id'], deleted_at__isnull=True)
            request.user = user
            request.user_id = user.id
        except User.DoesNotExist:
            request.user = None
            request.user_id = None

        return None
