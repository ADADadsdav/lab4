from django.db import models
from django.utils import timezone
import bcrypt
import os
import secrets


class UserManager(models.Manager):
    """Менеджер для активных пользователей"""

    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)


class User(models.Model):
    """Модель пользователя"""
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']  # Поля, которые запрашиваются при createsuperuser

    email = models.EmailField(unique=True, null=True, blank=True)
    phone = models.CharField(max_length=20, unique=True, null=True, blank=True)
    username = models.CharField(max_length=150, unique=True)

    # Поля для аутентификации
    password_hash = models.CharField(max_length=128, null=True, blank=True)
    password_salt = models.CharField(max_length=32, null=True, blank=True)

    # OAuth поля
    yandex_id = models.CharField(max_length=255, unique=True, null=True, blank=True)

    # Временные метки
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    # Менеджеры
    objects = models.Manager()
    active_objects = UserManager()

    @property
    def is_anonymous(self):
        return False

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return self.deleted_at is None

    class Meta:
        db_table = 'users'

    def set_password(self, raw_password: str):
        """Установка пароля с уникальной солью"""
        # Генерируем уникальную соль для каждого пароля
        salt = bcrypt.gensalt()
        # Хешируем пароль с солью
        password_hash = bcrypt.hashpw(raw_password.encode('utf-8'), salt)

        self.password_salt = salt.decode('utf-8')
        self.password_hash = password_hash.decode('utf-8')

    def check_password(self, raw_password: str) -> bool:
        """Проверка пароля"""
        if not self.password_hash or not self.password_salt:
            return False

        try:
            # Используем сохраненную соль для проверки
            salt = self.password_salt.encode('utf-8')
            password_hash = self.password_hash.encode('utf-8')
            return bcrypt.checkpw(raw_password.encode('utf-8'), password_hash)
        except Exception:
            return False

    def soft_delete(self):
        """Мягкое удаление пользователя"""
        self.deleted_at = timezone.now()
        self.save()

    def __str__(self):
        return f"{self.username} ({self.email or self.phone})"



class UserToken(models.Model):
    """Модель для хранения токенов"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tokens')
    token_hash = models.CharField(max_length=128)  # Хеш токена
    token_type = models.CharField(max_length=20, choices=[('access', 'Access'), ('refresh', 'Refresh')])
    expires_at = models.DateTimeField()
    is_revoked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_tokens'
        indexes = [
            models.Index(fields=['user', 'token_type', 'is_revoked']),
            models.Index(fields=['expires_at']),
        ]

    def is_valid(self) -> bool:
        """Проверка валидности токена"""
        return not self.is_revoked and self.expires_at > timezone.now()

    @staticmethod
    def hash_token(token: str) -> str:
        """Хеширование токена для хранения в БД"""
        import hashlib
        return hashlib.sha256(token.encode('utf-8')).hexdigest()


class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=64, unique=True)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)