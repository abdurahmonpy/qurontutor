from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Avg, Count
from .models import TelegramUser, Surah, Ayah, RecitationAttempt, UserProgress

# Admin Branding
admin.site.site_header = "Qur'on Tilovat Murabbiyi • Boshqaruv Paneli"
admin.site.site_title = "Qur'on Tilovat Admin"
admin.site.index_title = "Loyiha Ma'lumotlari va Tilovat Statistikasi"


class AyahInline(admin.TabularInline):
    model = Ayah
    extra = 0
    fields = ('number_in_surah', 'text_arabic_tajweed', 'text_translit', 'audio_preview')
    readonly_fields = ('number_in_surah', 'text_arabic_tajweed', 'text_translit', 'audio_preview')
    can_delete = False

    def audio_preview(self, obj):
        if obj.official_audio_url:
            return format_html(
                '<audio controls style="height: 30px; width: 180px;"><source src="{}" type="audio/mpeg"></audio>',
                obj.official_audio_url
            )
        return "-"
    audio_preview.short_description = "Audio"


@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = (
        'telegram_id', 'full_name', 'username_display',
        'current_location', 'attempts_count_display', 'avg_score_display', 'created_at'
    )
    search_fields = ('telegram_id', 'username', 'first_name', 'last_name')
    list_filter = ('current_surah_number', 'created_at')
    readonly_fields = ('telegram_id', 'created_at')

    def full_name(self, obj):
        name = f"{obj.first_name} {obj.last_name}".strip()
        return name or f"Foydalanuvchi #{obj.telegram_id}"
    full_name.short_description = "Foydalanuvchi"

    def username_display(self, obj):
        if obj.username:
            return format_html('<a href="https://t.me/{}" target="_blank">@{}</a>', obj.username, obj.username)
        return "-"
    username_display.short_description = "Telegram"

    def current_location(self, obj):
        return f"{obj.current_surah_number}-sura, {obj.current_ayah_number}-oyat"
    current_location.short_description = "Hozirgi Oyat"

    def attempts_count_display(self, obj):
        try:
            count = obj.attempts.count()
            return format_html('<b>{} ta</b> urinish', count)
        except Exception:
            return "0 ta"
    attempts_count_display.short_description = "Tilovatlar"

    def avg_score_display(self, obj):
        try:
            avg = obj.attempts.aggregate(Avg('score'))['score__avg']
            if avg is not None:
                color = "#15803d" if avg >= 80 else "#b45309" if avg >= 60 else "#b91c1c"
                formatted_avg = f"{float(avg):.1f}%"
                return format_html('<span style="color: {}; font-weight: bold;">{}</span>', color, formatted_avg)
            return "-"
        except Exception:
            return "-"
    avg_score_display.short_description = "O'rtacha Ball"


@admin.register(Surah)
class SurahAdmin(admin.ModelAdmin):
    list_display = ('number', 'name_uz', 'arabic_display', 'total_ayahs', 'revelation_badge', 'completed_users')
    search_fields = ('name_uz', 'name_arabic', 'name_english', 'number')
    list_filter = ('revelation_place',)
    inlines = [AyahInline]

    def arabic_display(self, obj):
        return format_html('<span style="font-size: 1.2rem; font-family: serif; color: #d97706;">{}</span>', obj.name_arabic)
    arabic_display.short_description = "Arabcha Nomi"

    def revelation_badge(self, obj):
        is_makkah = (obj.revelation_place or '').lower() == 'makkah'
        bg = '#fef3c7' if is_makkah else '#e0e7ff'
        color = '#b45309' if is_makkah else '#3730a3'
        text = 'Makkiy' if is_makkah else 'Madaniy'
        return format_html(
            '<span style="background: {}; color: {}; padding: 3px 8px; border-radius: 6px; font-weight: 600; font-size: 11px;">{}</span>',
            bg, color, text
        )
    revelation_badge.short_description = "Nozil Bo'lgan Joyi"

    def completed_users(self, obj):
        return UserProgress.objects.filter(surah=obj, status='completed').values('user').distinct().count()
    completed_users.short_description = "Tugatganlar Soni"


@admin.register(Ayah)
class AyahAdmin(admin.ModelAdmin):
    list_display = ('surah_display', 'number_in_surah', 'arabic_text_preview', 'translit_preview', 'audio_listen')
    list_filter = ('surah',)
    search_fields = ('text_arabic_clean', 'text_translit', 'text_translation_uz')
    readonly_fields = ('audio_listen',)

    def surah_display(self, obj):
        return f"{obj.surah.number}. {obj.surah.name_uz}"
    surah_display.short_description = "Sura"

    def arabic_text_preview(self, obj):
        text = obj.text_arabic_tajweed or obj.text_arabic_clean
        preview = (text[:60] + '...') if len(text) > 60 else text
        return format_html('<span style="font-family: serif; font-size: 1.1rem; color: #18181b;">{}</span>', preview)
    arabic_text_preview.short_description = "Oyat Matni"

    def translit_preview(self, obj):
        return (obj.text_translit[:50] + '...') if len(obj.text_translit) > 50 else obj.text_translit
    translit_preview.short_description = "O'qilishi"

    def audio_listen(self, obj):
        if obj.official_audio_url:
            return format_html(
                '<audio controls style="height: 32px; width: 220px;"><source src="{}" type="audio/mpeg"></audio>',
                obj.official_audio_url
            )
        return "-"
    audio_listen.short_description = "Qiroat Audiosi"


@admin.register(RecitationAttempt)
class RecitationAttemptAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_info', 'ayah_info', 'score_badge', 'audio_playback', 'created_at')
    list_filter = ('score', 'created_at', 'ayah__surah')
    search_fields = ('user__telegram_id', 'user__username', 'user__first_name', 'overall_feedback')
    readonly_fields = ('audio_playback_detail', 'formatted_word_results', 'created_at')

    def user_info(self, obj):
        if obj.user:
            return f"{obj.user.first_name} (@{obj.user.username or obj.user.telegram_id})"
        return "Noma'lum"
    user_info.short_description = "Foydalanuvchi"

    def ayah_info(self, obj):
        return f"{obj.ayah.surah.name_uz} ({obj.ayah.number_in_surah}-oyat)"
    ayah_info.short_description = "Oyat"

    def score_badge(self, obj):
        if obj.score >= 85:
            bg, color = '#dcfce7', '#15803d'
            label = "A'lo"
        elif obj.score >= 60:
            bg, color = '#fef3c7', '#b45309'
            label = "O'rtacha"
        else:
            bg, color = '#fee2e2', '#b91c1c'
            label = "Xato"

        return format_html(
            '<span style="background: {}; color: {}; padding: 3px 10px; border-radius: 12px; font-weight: bold; font-size: 12px;">{}% • {}</span>',
            bg, color, obj.score, label
        )
    score_badge.short_description = "Natija"

    def audio_playback(self, obj):
        if obj.audio_file:
            return format_html(
                '<audio controls style="height: 32px; width: 200px;"><source src="{}" type="audio/webm"></audio>',
                obj.audio_file.url
            )
        return "-"
    audio_playback.short_description = "Foydalanuvchi Audiosi"

    def audio_playback_detail(self, obj):
        return self.audio_playback(obj)
    audio_playback_detail.short_description = "Yozilgan Audio"

    def formatted_word_results(self, obj):
        if not obj.word_level_result or not isinstance(obj.word_level_result, list):
            return "So'zma-so'z natija mavjud emas."

        rows = []
        for w in obj.word_level_result:
            status = w.get('status', 'correct')
            word = w.get('word', '')
            spoken = w.get('spoken', '-')
            sim = w.get('similarity', 1.0)
            issues = ", ".join([i.get('message_uz', i.get('rule', '')) for i in w.get('tajweed_issues', [])]) or "-"

            bg = "#dcfce7" if status == 'correct' else "#fef3c7" if status == 'tajweed_issue' else "#fee2e2"
            color = "#15803d" if status == 'correct' else "#b45309" if status == 'tajweed_issue' else "#b91c1c"

            rows.append(
                f'<tr style="background: {bg}; color: {color};">'
                f'<td style="padding: 8px; font-weight: bold; font-family: serif; font-size: 1.1rem;">{word}</td>'
                f'<td style="padding: 8px;">{spoken or "-"}</td>'
                f'<td style="padding: 8px;">{int(sim * 100)}%</td>'
                f'<td style="padding: 8px; font-weight: 600;">{status}</td>'
                f'<td style="padding: 8px;">{issues}</td>'
                f'</tr>'
            )

        table_html = (
            '<table style="width: 100%; border-collapse: collapse; border: 1px solid #e5e7eb; font-size: 12px;">'
            '<thead style="background: #f3f4f6; text-align: left;">'
            '<tr><th style="padding: 8px;">Asl So\'z</th><th style="padding: 8px;">O\'qilgan</th><th style="padding: 8px;">Moslik</th><th style="padding: 8px;">Holat</th><th style="padding: 8px;">Tajvid Izohi</th></tr>'
            '</thead><tbody>' + "".join(rows) + '</tbody></table>'
        )
        return format_html(table_html)
    formatted_word_results.short_description = "Har Bir So'z Tahlili"


@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'surah', 'ayah', 'status_badge', 'best_score_badge', 'attempts_count', 'updated_at')
    list_filter = ('status', 'surah', 'updated_at')
    search_fields = ('user__telegram_id', 'user__username', 'user__first_name')

    def status_badge(self, obj):
        is_completed = obj.status == 'completed'
        bg = '#dcfce7' if is_completed else '#fef3c7'
        color = '#15803d' if is_completed else '#b45309'
        text = "Tugatilgan" if is_completed else "O'rganilmoqda"
        return format_html(
            '<span style="background: {}; color: {}; padding: 3px 8px; border-radius: 6px; font-weight: 600; font-size: 11px;">{}</span>',
            bg, color, text
        )
    status_badge.short_description = "Holat"

    def best_score_badge(self, obj):
        color = "#15803d" if obj.best_score >= 80 else "#b45309" if obj.best_score >= 60 else "#b91c1c"
        return format_html('<span style="color: {}; font-weight: bold;">{}%</span>', color, obj.best_score)
    best_score_badge.short_description = "Eng Yaxshi Ball"
