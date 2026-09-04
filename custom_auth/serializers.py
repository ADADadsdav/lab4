from rest_framework import serializers
from users.models import User
import re


class RegisterSerializer(serializers.Serializer):
    """Сериализатор для регистрации"""
    email = serializers.EmailField(required=False)  # Теперь необязательно
    phone = serializers.CharField(max_length=20, required=False)
    username = serializers.CharField(max_length=150, required=True)
    password = serializers.CharField(write_only=True, min_length=8, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        # Проверка: должен быть или email, или телефон
        if not data.get('email') and not data.get('phone'):
            raise serializers.ValidationError({
                'email': 'Необходимо указать email или телефон',
                'phone': 'Необходимо указать email или телефон'
            })

        # Проверка уникальности email
        email = data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise serializers.ValidationError({'email': 'Email уже зарегистрирован'})

        # Проверка уникальности телефона
        phone = data.get('phone')
        if phone and User.objects.filter(phone=phone).exists():
            raise serializers.ValidationError({'phone': 'Телефон уже зарегистрирован'})

        # Проверка уникальности username
        username = data.get('username')
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError({'username': 'Username уже занят'})

        # Валидация username
        if len(username) < 3:
            raise serializers.ValidationError({'username': 'Username должен быть не менее 3 символов'})
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            raise serializers.ValidationError({'username': 'Username может содержать только буквы, цифры и _'})

        # Валидация пароля
        password = data.get('password')
        if len(password) < 8:
            raise serializers.ValidationError({'password': 'Пароль должен быть не менее 8 символов'})
        if not re.search(r'[A-Z]', password):
            raise serializers.ValidationError({'password': 'Пароль должен содержать хотя бы одну заглавную букву'})
        if not re.search(r'[a-z]', password):
            raise serializers.ValidationError({'password': 'Пароль должен содержать хотя бы одну строчную букву'})
        if not re.search(r'\d', password):
            raise serializers.ValidationError({'password': 'Пароль должен содержать хотя бы одну цифру'})

        # Проверка совпадения паролей
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({'confirm_password': 'Пароли не совпадают'})

        return data

class LoginSerializer(serializers.Serializer):
    """Сериализатор для входа (email, телефон или username)"""
    identifier = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True)

class UserResponseSerializer(serializers.ModelSerializer):
    """Сериализатор для ответа с данными пользователя"""

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'created_at']
        read_only_fields = fields


class ForgotPasswordSerializer(serializers.Serializer):
    """Сериализатор для запроса сброса пароля"""
    email = serializers.EmailField(required=True)


class ResetPasswordSerializer(serializers.Serializer):
    """Сериализатор для сброса пароля"""
    token = serializers.CharField(required=True)
    new_password = serializers.CharField(min_length=8, required=True)
    confirm_password = serializers.CharField(required=True)

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({'confirm_password': 'Пароли не совпадают'})
        return data


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

class ResetPasswordSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)
    new_password = serializers.CharField(min_length=8, required=True)
    confirm_password = serializers.CharField(required=True)

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({'confirm_password': 'Пароли не совпадают'})
        return data