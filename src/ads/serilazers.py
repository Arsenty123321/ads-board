from rest_framework import serializers

from ads.models import Advertisement, Feedback


class AdSerializer(serializers.ModelSerializer):
    """Сериализатор модели объявления."""

    owner = serializers.PrimaryKeyRelatedField(read_only=True)

    def create(self, validated_data):
        """Добавление автора объявления."""
        validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)

    class Meta:
        model = Advertisement
        fields = '__all__'


class AdListSerializer(serializers.ModelSerializer):
    """Сериализатор для списка объявлений."""

    class Meta:
        model = Advertisement
        fields = ('id', 'title', 'price', 'created_at')  # Исключаем поле description и owner


class FeedbackSerializer(serializers.ModelSerializer):
    """Сериализатор модели отзыва."""
    owner = serializers.PrimaryKeyRelatedField(read_only=True)
    ad = serializers.PrimaryKeyRelatedField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)

    def create(self, validated_data):
        # Получаем текущего пользователя из контекста запроса
        user = self.context['request'].user
        # Получаем id объявления из контекста запроса
        ad_id = self.context['ad_id']
        # Проверяем существование объявления
        try:
            advertisement = Advertisement.objects.get(id=ad_id)
        except Advertisement.DoesNotExist:
            raise serializers.ValidationError({"ad_id": f"Объявления с id={ad_id} не существует."})

        feedback = Feedback.objects.create(owner=user, ad=advertisement, **validated_data)
        return feedback

    class Meta:
        model = Feedback
        fields = '__all__'
