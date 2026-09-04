from django.http import HttpResponseNotFound, HttpResponseBadRequest, HttpResponseServerError
from django.shortcuts import render
from rest_framework import viewsets, status, pagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Movie
from .serializers import *
from .services import MovieService
from custom_auth.permissions import IsCookieAuthenticated, CookieAuthentication

def index(request):
    movies = Movie.active_objects.all()
    return render(request, "movies/index.html", {"movies": movies})

# ---------- Обработчики ошибок ----------
def pageNotFound(request, exception):
    return HttpResponseNotFound('<h1>Ресурс не найден</h1>')

def pageBadRequest(request, exception):
    return HttpResponseBadRequest('<h1>Неверный формат данных</h1>')

def pageServerError(request):
    return HttpResponseServerError('<h1>Внутренняя ошибка сервера</h1>')
# ---------- Валидация параметров пагинации ----------

def validate_pagination_params(page, limit):
    errors = {}
    try:
        page = int(page) if page else 1
        if page < 1:
            errors['page'] = "Параметр page должен быть больше 0"
    except ValueError:
        errors['page'] = "Параметр page должен быть числом"
    try:
        limit = int(limit) if limit else 10
        if limit < 1 or limit > 100:
            errors['limit'] = "Параметр limit должен быть от 1 до 100"
    except ValueError:
        errors['limit'] = "Параметр limit должен быть числом"
    return errors, page if 'page' not in errors else 1, limit if 'limit' not in errors else 10


# ---------- API для второй лабораторной ----------
class CustomPagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = 'limit'
    max_page_size = 100
    page_query_param = 'page'

    def get_paginated_response(self, data):
        return Response({
            'data': data,
            'meta': {
                'total': self.page.paginator.count,
                'page': self.page.number,
                'limit': self.page_size,
                'totalPages': self.page.paginator.num_pages,
            }
        })

class MovieViewSet(viewsets.ViewSet):
    """
    GET    /api/movies/          - список с пагинацией
    GET    /api/movies/{id}/     - получить один фильм
    POST   /api/movies/          - создать фильм
    PUT    /api/movies/{id}/     - полное обновление
    PATCH  /api/movies/{id}/     - частичное обновление
    DELETE /api/movies/{id}/     - мягкое удаление
    """
    # Все операции с фильмами доступны только вошедшим пользователям.
    permission_classes = [IsCookieAuthenticated]
    authentication_classes = [CookieAuthentication]
    pagination_class = CustomPagination

    def list(self, request):
        """GET /movies/ - список всех активных фильмов с пагинацией"""
        page = request.query_params.get('page', 1)
        limit = request.query_params.get('limit', 10)
        errors, page, limit = validate_pagination_params(page, limit)
        if errors:
            return Response({'errors': errors}, status=status.HTTP_400_BAD_REQUEST)

        movies = MovieService.get_active_movies()
        paginator = self.pagination_class()
        paginator.page_size = limit
        page = paginator.paginate_queryset(movies, request)
        serializer = MovieOutputSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        """GET /movies/{id}/ - получить конкретный фильм"""
        try:
            movie = MovieService.get_active_movie_by_id(pk)
            # Проверяем владение
            if movie.user != request.user:
                return Response({'error': 'Доступ запрещен'}, status=status.HTTP_403_FORBIDDEN)
            serializer = MovieOutputSerializer(movie)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception:
            return Response({'error': 'Фильм не найден'}, status=status.HTTP_404_NOT_FOUND)

    def create(self, request):
        """POST /movies/ - создать новый фильм"""
        serializer = MovieCreateSerializer(data=request.data)
        if serializer.is_valid():
            # Создаём фильм с привязкой к пользователю
            movie = Movie.objects.create(
                user=request.user,
                **serializer.validated_data
            )
            output_serializer = MovieOutputSerializer(movie)
            return Response(output_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        """PUT /movies/{id}/ - полностью обновить фильм"""
        try:
            movie = MovieService.get_active_movie_by_id(pk)
            # Проверяем владение
            if movie.user != request.user:
                return Response({'error': 'Доступ запрещен'}, status=status.HTTP_403_FORBIDDEN)

            serializer = MovieUpdateSerializer(data=request.data)
            if serializer.is_valid():
                updated_movie = MovieService.update_movie(movie, serializer.validated_data)
                output_serializer = MovieOutputSerializer(updated_movie)
                return Response(output_serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response({'error': 'Фильм не найден'}, status=status.HTTP_404_NOT_FOUND)

    def partial_update(self, request, pk=None):
        """PATCH /movies/{id}/ - частично обновить фильм"""
        try:
            movie = MovieService.get_active_movie_by_id(pk)
            # Проверяем владение
            if movie.user != request.user:
                return Response({'error': 'Доступ запрещен'}, status=status.HTTP_403_FORBIDDEN)

            serializer = MoviePatchSerializer(data=request.data, partial=True)
            if serializer.is_valid():
                updated_movie = MovieService.update_movie(movie, serializer.validated_data)
                output_serializer = MovieOutputSerializer(updated_movie)
                return Response(output_serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response({'error': 'Фильм не найден'}, status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, pk=None):
        """DELETE /movies/{id}/ - мягкое удаление"""
        try:
            movie = MovieService.get_active_movie_by_id(pk)
            # Проверяем владение
            if movie.user != request.user:
                return Response({'error': 'Доступ запрещен'}, status=status.HTTP_403_FORBIDDEN)

            MovieService.soft_delete_movie(movie)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception:
            return Response({'error': 'Фильм не найден'}, status=status.HTTP_404_NOT_FOUND)
