from rest_framework import serializers

from ads.models import Advertisement


class AdsSerializer(serializers.ModelSerializer):
    """Сериализатор модели объявлений."""

    author = serializers.PrimaryKeyRelatedField(read_only=True)

    def create(self, validated_data):
        """Добавление автора объявления."""
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)

    class Meta:
        model = Advertisement
        fields = '__all__'


class AdsListSerializer(serializers.ModelSerializer):
    """Сериализатор для списка объявлений."""

    class Meta:
        model = Advertisement
        fields = ('id', 'title', 'price', 'created_at')  # Исключаем поле description и author
