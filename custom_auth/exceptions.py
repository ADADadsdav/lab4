from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        # Заменяем стандартные сообщения на безопасные
        if response.status_code == 401:
            response.data = {'error': 'Требуется авторизация'}
        elif response.status_code == 403:
            response.data = {'error': 'Доступ запрещен'}
        elif response.status_code == 500:
            response.data = {'error': 'Внутренняя ошибка сервера'}

    return response