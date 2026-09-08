import csv
from django.contrib import admin
from django.http import HttpResponse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.db.models import Avg, Count
from django.utils import timezone
from .models import TelegramUser, Surah, Ayah, RecitationAttempt, UserProgress, BroadcastMessage
from .telegram_service import broadcast_to_users

# Admin Branding
admin.site.site_header = "Qur'on Tilovat Murabbiyi • Boshqaruv Paneli"
admin.site.site_title = "Qur'on Tilovat Admin"
admin.site.index_title = "Loyiha Ma'lumotlari va Tilovat Statistikasi"


# -------------------------------------------------------------
# CSV Export Helper Actions
# -------------------------------------------------------------
def export_users_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="telegram_foydalanuvchilar.csv"'
    response.write('\ufeff')  # UTF-8 BOM for Microsoft Excel
    writer = csv.writer(response)
    writer.writerow(['Telegram ID', 'Foydalanuvchi Nomi', 'Username', 'Joriy Sura', 'Joriy Oyat', 'Tilovatlar Soni', "O'rtacha Ball (%)", "Ro'yxatdan O'tgan Sana"])
    
    for u in queryset:
        try:
            attempts_count = u.attempts.count()
            avg_score = u.attempts.aggregate(Avg('score'))['score__avg']
            avg_str = f"{avg_score:.1f}" if avg_score is not None else "-"
        except Exception:
            attempts_count = 0
            avg_str = "-"

        writer.writerow([
            u.telegram_id,
            f"{u.first_name} {u.last_name}".strip() or f"Foydalanuvchi #{u.telegram_id}",
            f"@{u.username}" if u.username else "-",
            u.current_surah_number,
            u.current_ayah_number,
            attempts_count,
            avg_str,
            u.created_at.strftime('%Y-%m-%d %H:%M') if u.created_at else "-"
        ])
    return response
export_users_csv.short_description = "📥 Tanlangan foydalanuvchilarni CSV (Excel) ga yuklab olish"


def export_attempts_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="tilovatlar_hisoboti.csv"'
    response.write('\ufeff')
    writer = csv.writer(response)
    writer.writerow(['ID', 'Foydalanuvchi ID', 'Ismi', 'Sura', 'Oyat', 'Ball (%)', 'Baho', 'Sana'])
    
    for a in queryset:
        user_id = a.user.telegram_id if a.user else "-"
        user_name = a.user.first_name if a.user else "Noma'lum"
        surah_name = a.ayah.surah.name_uz if a.ayah and a.ayah.surah else "-"
        ayah_num = a.ayah.number_in_surah if a.ayah else "-"
        grade = "A'lo" if a.score >= 85 else "O'rtacha" if a.score >= 60 else "Xato"
        writer.writerow([
            a.id,
            user_id,
            user_name,
            surah_name,
            ayah_num,
            a.score,
            grade,
            a.created_at.strftime('%Y-%m-%d %H:%M') if a.created_at else "-"
        ])
    return response
export_attempts_csv.short_description = "📥 Tanlangan tilovatlarni CSV (Excel) ga yuklab olish"


# -------------------------------------------------------------
# Inlines & Custom Filters
# -------------------------------------------------------------
class AyahInline(admin.TabularInline):
    model = Ayah
    extra = 0
    fields = ('number_in_surah', 'text_arabic_tajweed', 'text_translit', 'audio_preview')
    readonly_fields = ('number_in_surah', 'text_arabic_tajweed', 'text_translit', 'audio_preview')
    can_delete = False

    def audio_preview(self, obj):
        if obj.official_audio_url:
            return format_html(
                '<audio controls preload="none" style="height: 28px; width: 180px;" src="{}"></audio>',
                obj.official_audio_url
            )
        return "-"
    audio_preview.short_description = "Audio"


class ScoreRangeFilter(admin.SimpleListFilter):
    title = "Natija Darajasi"
    parameter_name = "score_grade"

    def lookups(self, request, model_admin):
        return (
            ('excellent', "🟢 A'lo (85% — 100%)"),
            ('good', "🟡 O'rtacha (60% — 84%)"),
            ('needs_work', "🔴 Qayta topshirish (< 60%)"),
        )

    def queryset(self, request, queryset):
        if self.value() == 'excellent':
            return queryset.filter(score__gte=85)
        if self.value() == 'good':
            return queryset.filter(score__gte=60, score__lt=85)
        if self.value() == 'needs_work':
            return queryset.filter(score__lt=60)
        return queryset


# -------------------------------------------------------------
# TelegramUser Admin
# -------------------------------------------------------------
@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = (
        'telegram_id', 'full_name', 'username_display',
        'current_location', 'attempts_count_display', 'avg_score_display', 'created_at'
    )
    search_fields = ('telegram_id', 'username', 'first_name', 'last_name')
    list_filter = ('current_surah_number', 'created_at')
    readonly_fields = ('telegram_id', 'created_at')
    actions = [export_users_csv, 'send_reminder_action']

    def full_name(self, obj):
        name = f"{obj.first_name} {obj.last_name}".strip()
        return name or f"Foydalanuvchi #{obj.telegram_id}"
    full_name.short_description = "Foydalanuvchi"

    def username_display(self, obj):
        if obj.username:
            return format_html('<a href="https://t.me/{}" target="_blank" style="color: #38bdf8; font-weight: 600;">@{}</a>', obj.username, obj.username)
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
                color = "#22c55e" if avg >= 80 else "#f59e0b" if avg >= 60 else "#ef4444"
                formatted_avg = f"{float(avg):.1f}%"
                return format_html('<span style="color: {}; font-weight: bold;">{}</span>', color, formatted_avg)
            return "-"
        except Exception:
            return "-"
    avg_score_display.short_description = "O'rtacha Ball"

    def send_reminder_action(self, request, queryset):
        text = "Assalomu alaykum, muhtaram {name}! Qur'on tilovatingizni davom ettirish va yangi oyatlarni topshirish uchun botimizga kiring: @qurontutorbot"
        sent, failed, errors = broadcast_to_users(
            user_qs=queryset,
            text=text,
            button_text="📖 Tilovatni Boshlash",
            button_url="https://t.me/qurontutorbot"
        )
        self.message_user(
            request,
            f"Belgilangan {queryset.count()} ta foydalanuvchiga eslatma xabari yuborildi: {sent} ta muvaffaqiyatli, {failed} ta xatolik."
        )
    send_reminder_action.short_description = "✉️ Tanlanganlarga tilovat eslatmasini yuborish"


# -------------------------------------------------------------
# Surah & Ayah Admins
# -------------------------------------------------------------
@admin.register(Surah)
class SurahAdmin(admin.ModelAdmin):
    list_display = ('number', 'name_uz', 'arabic_display', 'total_ayahs', 'revelation_badge', 'completed_users')
    search_fields = ('name_uz', 'name_arabic', 'name_english', 'number')
    list_filter = ('revelation_place',)
    inlines = [AyahInline]

    def arabic_display(self, obj):
        return format_html('<span style="font-size: 1.25rem; font-family: serif; color: #fbbf24;">{}</span>', obj.name_arabic)
    arabic_display.short_description = "Arabcha Nomi"

    def revelation_badge(self, obj):
        is_makkah = (obj.revelation_place or '').lower() == 'makkah'
        bg = 'rgba(245, 158, 11, 0.15)' if is_makkah else 'rgba(59, 130, 246, 0.15)'
        color = '#fbbf24' if is_makkah else '#60a5fa'
        border = '#d97706' if is_makkah else '#2563eb'
        text = 'Makkiy' if is_makkah else 'Madaniy'
        return format_html(
            '<span style="background: {}; color: {}; border: 1px solid {}; padding: 3px 8px; border-radius: 6px; font-weight: 600; font-size: 11px;">{}</span>',
            bg, color, border, text
        )
    revelation_badge.short_description = "Nozil Bo'lgan Joyi"

    def completed_users(self, obj):
        try:
            return UserProgress.objects.filter(surah=obj, status='completed').values('user').distinct().count()
        except Exception:
            return 0
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
        text = obj.text_arabic_tajweed or obj.text_arabic_clean or ""
        preview = (text[:60] + '...') if len(text) > 60 else text
        return format_html('<span style="font-family: serif; font-size: 1.15rem; color: #f8fafc;">{}</span>', preview)
    arabic_text_preview.short_description = "Oyat Matni"

    def translit_preview(self, obj):
        text = obj.text_translit or ""
        return (text[:50] + '...') if len(text) > 50 else text
    translit_preview.short_description = "O'qilishi"

    def audio_listen(self, obj):
        if obj.official_audio_url:
            return format_html(
                '<audio controls preload="none" style="height: 30px; width: 210px;" src="{}"></audio>',
                obj.official_audio_url
            )
        return "-"
    audio_listen.short_description = "Qiroat Audiosi"


# -------------------------------------------------------------
# RecitationAttempt Admin
# -------------------------------------------------------------
@admin.register(RecitationAttempt)
class RecitationAttemptAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user_info', 'ayah_info', 'score_badge',
        'audio_playback', 'official_audio_sample', 'created_at'
    )
    list_filter = (ScoreRangeFilter, 'created_at', 'ayah__surah')
    search_fields = ('user__telegram_id', 'user__username', 'user__first_name', 'overall_feedback')
    readonly_fields = ('audio_playback_detail', 'official_audio_sample', 'formatted_word_results', 'created_at')
    actions = [export_attempts_csv]

    def user_info(self, obj):
        if obj.user:
            return f"{obj.user.first_name} (@{obj.user.username or obj.user.telegram_id})"
        return "Noma'lum"
    user_info.short_description = "Foydalanuvchi"

    def ayah_info(self, obj):
        try:
            return f"{obj.ayah.surah.name_uz} ({obj.ayah.number_in_surah}-oyat)"
        except Exception:
            return f"Oyat #{getattr(obj, 'ayah_id', '-')}"
    ayah_info.short_description = "Oyat"

    def score_badge(self, obj):
        score = obj.score or 0
        if score >= 85:
            bg, color, border = 'rgba(34, 197, 94, 0.15)', '#4ade80', '#22c55e'
            label = "A'lo"
        elif score >= 60:
            bg, color, border = 'rgba(245, 158, 11, 0.15)', '#fbbf24', '#f59e0b'
            label = "O'rtacha"
        else:
            bg, color, border = 'rgba(239, 68, 68, 0.15)', '#f87171', '#ef4444'
            label = "Xato"

        return format_html(
            '<span style="background: {}; color: {}; border: 1px solid {}; padding: 3px 10px; border-radius: 12px; font-weight: bold; font-size: 11px;">{}% • {}</span>',
            bg, color, border, score, label
        )
    score_badge.short_description = "Natija"

    def audio_playback(self, obj):
        if obj.audio_file:
            try:
                url = obj.audio_file.url
                return format_html(
                    '<audio controls preload="none" style="height: 30px; width: 200px;" src="{}">'
                    'Brauzer audioni qo\'llab-quvvatlamaydi</audio>',
                    url
                )
            except Exception:
                return "-"
        return "-"
    audio_playback.short_description = "Foydalanuvchi Audiosi"

    def official_audio_sample(self, obj):
        if obj.ayah and obj.ayah.official_audio_url:
            return format_html(
                '<audio controls preload="none" style="height: 30px; width: 200px;" src="{}"></audio>',
                obj.ayah.official_audio_url
            )
        return "-"
    official_audio_sample.short_description = "Qori Qiroati (Namuna)"

    def audio_playback_detail(self, obj):
        if obj.audio_file:
            try:
                url = obj.audio_file.url
                return format_html(
                    '<div style="display: flex; flex-direction: column; gap: 8px;">'
                    '<audio controls style="height: 38px; width: 320px;" src="{}"></audio>'
                    '<a href="{}" target="_blank" download style="color: #fbbf24; font-weight: 600; font-size: 13px;">'
                    '📥 Ovoz faylini kompyuterga yuklab olish</a>'
                    '</div>',
                    url, url
                )
            except Exception:
                return "-"
        return "-"
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

            bg = "rgba(34, 197, 94, 0.12)" if status == 'correct' else "rgba(245, 158, 11, 0.12)" if status == 'tajweed_issue' else "rgba(239, 68, 68, 0.12)"
            color = "#4ade80" if status == 'correct' else "#fbbf24" if status == 'tajweed_issue' else "#f87171"

            rows.append(
                f'<tr style="background: {bg}; color: {color};">'
                f'<td style="padding: 8px; font-weight: bold; font-family: serif; font-size: 1.15rem;">{word}</td>'
                f'<td style="padding: 8px;">{spoken or "-"}</td>'
                f'<td style="padding: 8px;">{int(sim * 100)}%</td>'
                f'<td style="padding: 8px; font-weight: 600;">{status}</td>'
                f'<td style="padding: 8px;">{issues}</td>'
                f'</tr>'
            )

        table_html = (
            '<table style="width: 100%; border-collapse: collapse; border: 1px solid #334155; font-size: 12px; border-radius: 8px; overflow: hidden;">'
            '<thead style="background: #1e293b; color: #fbbf24; text-align: left;">'
            '<tr><th style="padding: 10px;">Asl So\'z</th><th style="padding: 10px;">O\'qilgan</th><th style="padding: 10px;">Moslik</th><th style="padding: 10px;">Holat</th><th style="padding: 10px;">Tajvid Izohi</th></tr>'
            '</thead><tbody>' + "".join(rows) + '</tbody></table>'
        )
        return mark_safe(table_html)
    formatted_word_results.short_description = "Har Bir So'z Tahlili"


# -------------------------------------------------------------
# UserProgress Admin
# -------------------------------------------------------------
@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'surah', 'ayah', 'status_badge', 'best_score_badge', 'attempts_count', 'updated_at')
    list_filter = ('status', 'surah', 'updated_at')
    search_fields = ('user__telegram_id', 'user__username', 'user__first_name')

    def status_badge(self, obj):
        is_completed = obj.status == 'completed'
        bg = 'rgba(34, 197, 94, 0.15)' if is_completed else 'rgba(245, 158, 11, 0.15)'
        color = '#4ade80' if is_completed else '#fbbf24'
        border = '#22c55e' if is_completed else '#f59e0b'
        text = "Tugatilgan" if is_completed else "O'rganilmoqda"
        return format_html(
            '<span style="background: {}; color: {}; border: 1px solid {}; padding: 3px 8px; border-radius: 6px; font-weight: 600; font-size: 11px;">{}</span>',
            bg, color, border, text
        )
    status_badge.short_description = "Holat"

    def best_score_badge(self, obj):
        score = obj.best_score or 0
        color = "#4ade80" if score >= 80 else "#fbbf24" if score >= 60 else "#f87171"
        return format_html('<span style="color: {}; font-weight: bold;">{}%</span>', color, score)
    best_score_badge.short_description = "Eng Yaxshi Ball"


# -------------------------------------------------------------
# BroadcastMessage Admin (Ommaviy Xabarnoma)
# -------------------------------------------------------------
@admin.register(BroadcastMessage)
class BroadcastMessageAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'target_badge', 'status_badge',
        'sent_count_display', 'created_at', 'sent_at'
    )
    list_filter = ('status', 'target_audience', 'created_at')
    search_fields = ('title', 'message_text')
    readonly_fields = ('sent_count', 'failed_count', 'error_summary', 'sent_at', 'created_at', 'message_preview')
    actions = ['send_broadcast_action']

    fieldsets = (
        ("Xabarnoma Mazmuni", {
            'fields': ('title', 'target_audience', 'message_text', 'photo'),
            'description': "Telegram orqali jo'natiladigan xabar matni va rasmini kiriting. Matnda HTML teglari (<b>qalin</b>, <i>kursiv</i>) hamda {name} shaxsiy ism o'zgaruvchisidan foydalanishingiz mumkin."
        }),
        ("Inline Tugma (Ixtiyoriy)", {
            'fields': ('button_text', 'button_url'),
            'description': "Xabar ostiga Telegram inline tugmasi joylashtirish mumkin."
        }),
        ("Xabar Ko'rinishi va Statistika", {
            'fields': ('message_preview', 'status', 'sent_count', 'failed_count', 'sent_at', 'created_at', 'error_summary'),
            'classes': ('collapse',)
        }),
    )

    def target_badge(self, obj):
        labels = {
            'all': ("Barcha foydalanuvchilar", "#0284c7"),
            'active': ("Faol qorilar", "#16a34a"),
            'inactive': ("Hali o'qimaganlar", "#d97706"),
        }
        text, color = labels.get(obj.target_audience, (obj.target_audience, "#6b7280"))
        return format_html(
            '<span style="background: rgba(255,255,255,0.06); border: 1px solid {}; color: {}; padding: 3px 8px; border-radius: 6px; font-weight: 600; font-size: 11px;">{}</span>',
            color, color, text
        )
    target_badge.short_description = "Auditoriya"

    def status_badge(self, obj):
        colors = {
            'draft': ('#64748b', 'Qoralama'),
            'sending': ('#0284c7', 'Yuborilmoqda...'),
            'sent': ('#16a34a', 'Yuborildi'),
            'failed': ('#dc2626', 'Xatolik'),
        }
        color, text = colors.get(obj.status, ('#64748b', obj.status))
        return format_html(
            '<span style="background: {}; color: #fff; padding: 3px 10px; border-radius: 12px; font-weight: 600; font-size: 11px;">{}</span>',
            color, text
        )
    status_badge.short_description = "Holat"

    def sent_count_display(self, obj):
        if obj.status == 'draft':
            return "-"
        return format_html(
            '<span style="color: #4ade80; font-weight: bold;">{} yetdi</span> / <span style="color: #f87171;">{} xato</span>',
            obj.sent_count, obj.failed_count
        )
    sent_count_display.short_description = "Yetkazildi / Xatolik"

    def message_preview(self, obj):
        try:
            img_html = ""
            if obj.photo:
                try:
                    img_html = f'<img src="{obj.photo.url}" style="max-width: 250px; border-radius: 8px; margin-bottom: 10px; display: block;">'
                except Exception:
                    img_html = ""

            btn_html = ""
            if obj.button_text and obj.button_url:
                btn_html = f'<div style="margin-top: 12px;"><a href="{obj.button_url}" target="_blank" style="background: #f59e0b; color: #000; font-weight: 600; padding: 6px 14px; border-radius: 6px; text-decoration: none; display: inline-block; font-size: 12px;">{obj.button_text}</a></div>'
            
            body_text = (obj.message_text or "<i>Xabar matni kiritilmagan</i>").replace('\n', '<br>')
            return mark_safe(
                f'<div style="background: #1e293b; padding: 16px; border-radius: 12px; border: 1px solid #334155; max-width: 450px; color: #f8fafc;">'
                f'{img_html}'
                f'<div>{body_text}</div>'
                f'{btn_html}'
                f'</div>'
            )
        except Exception as e:
            return f"Ko'rinish yuklanmadi: {e}"
    message_preview.short_description = "Xabar Ko'rinishi (Preview)"

    def send_broadcast_action(self, request, queryset):
        total_sent = 0
        total_failed = 0

        for msg in queryset:
            # Filter audience
            if msg.target_audience == 'active':
                users = TelegramUser.objects.filter(attempts__isnull=False).distinct()
            elif msg.target_audience == 'inactive':
                users = TelegramUser.objects.filter(attempts__isnull=True)
            else:
                users = TelegramUser.objects.all()

            msg.status = 'sending'
            msg.save()

            photo_file = msg.photo.file if msg.photo else None
            sent, failed, errors = broadcast_to_users(
                user_qs=users,
                text=msg.message_text,
                photo=photo_file,
                button_text=msg.button_text,
                button_url=msg.button_url
            )

            msg.sent_count = sent
            msg.failed_count = failed
            msg.status = 'sent' if sent > 0 or failed == 0 else 'failed'
            msg.sent_at = timezone.now()
            if errors:
                msg.error_summary = "\n".join(errors[:20])
            msg.save()

            total_sent += sent
            total_failed += failed

        self.message_user(
            request,
            f"Xabarnoma yakunlandi! Jami yetkazildi: {total_sent} ta, Yetib bormadi (bloklaganlar): {total_failed} ta."
        )

    send_broadcast_action.short_description = "📨 Tanlangan xabarnomalarni foydalanuvchilarga yuborish"
