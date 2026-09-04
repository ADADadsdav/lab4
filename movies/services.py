from django.shortcuts import get_object_or_404
from .models import Movie


class MovieService:
    """Сервисный слой для работы с фильмами"""

    @staticmethod
    def get_active_movies():
        """Получить все активные фильмы"""
        return Movie.active_objects.all()

    @staticmethod
    def get_active_movie_by_id(pk):
        """Получить активный фильм по ID или вернуть 404"""
        return get_object_or_404(Movie.active_objects.all(), pk=pk)

    @staticmethod
    def create_movie(data):
        """Создать новый фильм"""
        return Movie.objects.create(**data)

    @staticmethod
    def update_movie(movie, data):
        """Обновить фильм"""
        for field, value in data.items():
            setattr(movie, field, value)
        movie.save()
        return movie

    @staticmethod
    def soft_delete_movie(movie):
        """Мягкое удаление фильма"""
        movie.delete()  # использует наш soft delete
        return movie