from rest_framework import serializers

from ads.models import Advertisement, Feedback
from ads.tasks import send_feedback_notification_email
from config import settings


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

        # Отправка уведомления на email владельца объявления о новом отзыве
        if advertisement.owner and advertisement.owner.email:
            send_feedback_notification_email .delay(
                ad_title=advertisement.title,
                ad_owner_email=advertisement.owner.email,
                feedback_owner_email=user.email,
                feedback_text=feedback.text,
                feedback_created_at=str(feedback.created_at)
            )
            if settings.DEBUG:
                # DEBUG
                print(f"#### DEBUG: Sending a revocation notification to {advertisement.owner.email} from {user.email}")

        return feedback

    class Meta:
        model = Feedback
        fields = '__all__'
