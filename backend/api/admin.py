from django.contrib import admin
from .models import TelegramUser, Surah, Ayah, RecitationAttempt, UserProgress

@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ('telegram_id', 'username', 'first_name', 'current_surah_number', 'current_ayah_number', 'created_at')
    search_fields = ('telegram_id', 'username', 'first_name')

@admin.register(Surah)
class SurahAdmin(admin.ModelAdmin):
    list_display = ('number', 'name_uz', 'name_arabic', 'total_ayahs', 'revelation_place')
    search_fields = ('name_uz', 'name_arabic', 'name_english')

@admin.register(Ayah)
class AyahAdmin(admin.ModelAdmin):
    list_display = ('surah', 'number_in_surah', 'text_arabic_tajweed', 'text_translit')
    list_filter = ('surah',)
    search_fields = ('text_arabic_clean', 'text_translation_uz', 'text_translit')

@admin.register(RecitationAttempt)
class RecitationAttemptAdmin(admin.ModelAdmin):
    list_display = ('user', 'ayah', 'score', 'created_at')
    list_filter = ('score', 'created_at')
    search_fields = ('user__telegram_id', 'user__username')

@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'surah', 'ayah', 'status', 'best_score', 'attempts_count', 'updated_at')
    list_filter = ('status', 'surah')
