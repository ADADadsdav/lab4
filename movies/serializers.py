from rest_framework import serializers
from .models import Movie


class MovieOutputSerializer(serializers.ModelSerializer):
    """Для ответов (GET)"""

    class Meta:
        model = Movie
        fields = ['id', 'title', 'director', 'year', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class MovieCreateSerializer(serializers.ModelSerializer):
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