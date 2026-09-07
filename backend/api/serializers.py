from rest_framework import serializers
from .models import TelegramUser, Surah, Ayah, RecitationAttempt, UserProgress

class SurahSerializer(serializers.ModelSerializer):
    completed_ayahs_count = serializers.SerializerMethodField()

    class Meta:
        model = Surah
        fields = [
            'id', 'number', 'name_arabic', 'name_uz', 'name_english',
            'revelation_place', 'total_ayahs', 'completed_ayahs_count'
        ]

    def get_completed_ayahs_count(self, obj):
        user_id = self.context.get('telegram_id')
        if not user_id:
            return 0
        return UserProgress.objects.filter(
            user__telegram_id=user_id,
            surah=obj,
            status='completed'
        ).count()

class AyahSerializer(serializers.ModelSerializer):
    user_status = serializers.SerializerMethodField()
    best_score = serializers.SerializerMethodField()

    class Meta:
        model = Ayah
        fields = [
            'id', 'surah', 'number_in_surah', 'number_global',
            'text_arabic_tajweed', 'text_arabic_clean', 'text_translit',
            'text_translation_uz', 'official_audio_url', 'user_status', 'best_score'
        ]

    def get_user_status(self, obj):
        user_id = self.context.get('telegram_id')
        if not user_id:
            return 'not_started'
        progress = UserProgress.objects.filter(user__telegram_id=user_id, ayah=obj).first()
        return progress.status if progress else 'not_started'

    def get_best_score(self, obj):
        user_id = self.context.get('telegram_id')
        if not user_id:
            return 0
        progress = UserProgress.objects.filter(user__telegram_id=user_id, ayah=obj).first()
        return progress.best_score if progress else 0

class RecitationAttemptSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecitationAttempt
        fields = ['id', 'user', 'ayah', 'score', 'word_level_result', 'overall_feedback', 'created_at']

class UserProgressSerializer(serializers.ModelSerializer):
    surah_number = serializers.IntegerField(source='surah.number', read_only=True)
    ayah_number = serializers.IntegerField(source='ayah.number_in_surah', read_only=True)

    class Meta:
        model = UserProgress
        fields = ['surah', 'ayah', 'surah_number', 'ayah_number', 'status', 'attempts_count', 'best_score', 'updated_at']

class TelegramUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = TelegramUser
        fields = ['telegram_id', 'username', 'first_name', 'last_name', 'current_surah_number', 'current_ayah_number', 'created_at']
