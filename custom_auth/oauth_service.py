import requests
import secrets
from urllib.parse import urlencode
from django.conf import settings
from users.models import User
from .auth_service import AuthService


class OAuthService:
    """Сервис для OAuth аутентификации через Yandex"""

    @staticmethod
    def get_yandex_auth_url() -> tuple:
        """Получение URL для авторизации через Yandex и state для CSRF защиты"""
        state = secrets.token_urlsafe(32)

        params = {
            'response_type': 'code',
            'client_id': settings.YANDEX_CLIENT_ID,
            'redirect_uri': settings.YANDEX_CALLBACK_URL,
            'state': state
        }

        auth_url = f"https://oauth.yandex.ru/authorize?{urlencode(params)}"
        return auth_url, state

    @staticmethod
    def exchange_yandex_code(code: str) -> dict:
        """Обмен кода на токен доступа Yandex"""
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'client_id': settings.YANDEX_CLIENT_ID,
            'client_secret': settings.YANDEX_CLIENT_SECRET,
            'redirect_uri': settings.YANDEX_CALLBACK_URL
        }

        response = requests.post(
            'https://oauth.yandex.ru/token',
            data=data
        )

        if response.status_code != 200:
            raise Exception(f'Ошибка обмена кода на токен: {response.text}')

        return response.json()

    @staticmethod
    def get_yandex_user_info(access_token: str) -> dict:
        """Получение информации о пользователе от Yandex"""
        headers = {'Authorization': f'OAuth {access_token}'}
        response = requests.get(
            'https://login.yandex.ru/info',
            headers=headers,
            params={'format': 'json'}
        )

        if response.status_code != 200:
            raise Exception(f'Ошибка получения информации о пользователе: {response.text}')

        return response.json()

    @staticmethod
    def handle_yandex_oauth(code: str) -> dict:
        """Обработка OAuth callback от Yandex"""
        # Получаем access token Yandex
        token_data = OAuthService.exchange_yandex_code(code)

        # Получаем информацию о пользователе
        user_info = OAuthService.get_yandex_user_info(token_data['access_token'])

        # Ищем или создаем пользователя
        yandex_id = str(user_info.get('id'))
        user = User.active_objects.filter(yandex_id=yandex_id).first()

        if not user:
            # Создаем нового пользователя
            username = user_info.get('login', f"yandex_{yandex_id}")
            email = user_info.get('default_email')

            # Убеждаемся, что username уникален
            base_username = username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}_{counter}"
                counter += 1

            user = User.objects.create(
                username=username,
                email=email,
                yandex_id=yandex_id
            )

        # Генерируем JWT токены
        return AuthService.generate_tokens_for_user(user)