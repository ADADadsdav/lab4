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
        # Получаем пользователя
        try:
            user = User.objects.get(id=payload['user_id'], deleted_at__isnull=True)
            stored_token = next((candidate for candidate in UserToken.objects.filter(
                user=user, token_type='access', is_revoked=False
            ) if candidate.matches_token(access_token) and candidate.is_valid()), None)
            if not stored_token:
                request.user = None
                request.user_id = None
                return None
            request.user = user
            request.user_id = user.id
        except User.DoesNotExist:
            request.user = None
            request.user_id = None

        return None
