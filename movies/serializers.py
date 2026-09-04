from rest_framework import serializers
from .models import Movie
from drf_spectacular.utils import extend_schema_serializer, OpenApiExample


@extend_schema_serializer(
    examples=[OpenApiExample(
        'Movie response',
        value={
            'id': 1,
            'title': 'Inception',
            'director': 'Christopher Nolan',
            'year': 2010,
            'created_at': '2026-09-04T12:00:00Z',
            'updated_at': '2026-09-04T12:00:00Z',
        },
        response_only=True,
    )]
)
class MovieOutputSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True, help_text='Уникальный идентификатор фильма.')
    title = serializers.CharField(help_text='Название фильма.')
    director = serializers.CharField(help_text='Режиссёр фильма.')
    year = serializers.IntegerField(help_text='Год выпуска фильма.')
    created_at = serializers.DateTimeField(read_only=True, help_text='Дата создания записи.')
    updated_at = serializers.DateTimeField(read_only=True, help_text='Дата последнего изменения.')

    """Для ответов (GET)"""

    class Meta:
        model = Movie
        fields = ['id', 'title', 'director', 'year', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


@extend_schema_serializer(
    examples=[OpenApiExample(
        'Movie request',
        value={'title': 'Inception', 'director': 'Christopher Nolan', 'year': 2010},
        request_only=True,
    )]
)
class MovieCreateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(help_text='Название фильма, минимум 2 символа.')
    director = serializers.CharField(help_text='Режиссёр фильма.')
    year = serializers.IntegerField(help_text='Год выпуска от 1888 до текущего года + 5.')

    """Для создания (POST) с валидацией"""

    class Meta:
        model = Movie
        fields = ['title', 'director', 'year']  # user не включаем, он добавится в views

    def validate_year(self, value):
        from datetime import datetime
        current_year = datetime.now().year
        if value < 1888:
            raise serializers.ValidationError("Год должен быть не меньше 1888")
        if value > current_year + 5:
            raise serializers.ValidationError(f"Год не может быть больше {current_year + 5}")
        return value

    def validate_title(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Название должно быть не короче 2 символов")
        return value.strip()

class MovieUpdateSerializer(serializers.ModelSerializer):
    """Для полного обновления (PUT)"""

    class Meta:
        model = Movie
        fields = ['title', 'director', 'year']
        extra_kwargs = {
            'title': {'required': True, 'allow_blank': False},
            'director': {'required': True, 'allow_blank': False},
            'year': {'required': True}
        }

    def validate_year(self, value):
        from datetime import datetime
        current_year = datetime.now().year
        if value < 1888 or value > current_year + 5:
            raise serializers.ValidationError(f"Год должен быть между 1888 и {current_year + 5}")
        return value


class MoviePatchSerializer(serializers.ModelSerializer):
    """Для частичного обновления (PATCH)"""

    class Meta:
        model = Movie
        fields = ['title', 'director', 'year']
        extra_kwargs = {
            'title': {'required': False, 'allow_blank': False},
            'director': {'required': False, 'allow_blank': False},
            'year': {'required': False}
        }

    def validate_year(self, value):
        if value is not None:
            from datetime import datetime
            current_year = datetime.now().year
            if value < 1888 or value > current_year + 5:
                raise serializers.ValidationError(f"Год должен быть между 1888 и {current_year + 5}")
        return value


class PaginationMetaSerializer(serializers.Serializer):
    total = serializers.IntegerField(read_only=True)
    page = serializers.IntegerField(read_only=True)
    limit = serializers.IntegerField(read_only=True)
    totalPages = serializers.IntegerField(read_only=True)


class MovieListResponseSerializer(serializers.Serializer):
    data = MovieOutputSerializer(many=True, read_only=True)
    meta = PaginationMetaSerializer(read_only=True)
