from django.db import models
from django.utils import timezone
from django.conf import settings


class SoftDeleteManager(models.Manager):
    """Менеджер для активных (не удаленных) записей"""
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)

class Movie(models.Model):
    # id создается автоматически! (primary key)

    # Три содержательных поля (минимум 3)
    title = models.CharField(max_length=255)  # название
    director = models.CharField(max_length=255)  # режиссер
    year = models.IntegerField()  # год

    # Временные метки (автоматические)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # Поле для мягкого удаления
    deleted_at = models.DateTimeField(null=True, blank=True)

    # Менеджеры
    objects = models.Manager()
    active_objects = SoftDeleteManager()

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='movies',
        null=True  # временно для существующих фильмов
    )

    def delete(self):
        """Soft Delete - просто помечаем как удаленный"""
        self.deleted_at = timezone.now()
        self.save()

    def __str__(self):
        return f"{self.title} ({self.year})"
