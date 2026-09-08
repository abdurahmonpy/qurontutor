from django.db import models

class TelegramUser(models.Model):
    telegram_id = models.BigIntegerField(unique=True, db_index=True)
    username = models.CharField(max_length=255, null=True, blank=True)
    first_name = models.CharField(max_length=255, blank=True, default='')
    last_name = models.CharField(max_length=255, blank=True, default='')
    current_surah_number = models.PositiveIntegerField(default=1)
    current_ayah_number = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} (@{self.username or self.telegram_id})"

class Surah(models.Model):
    number = models.PositiveIntegerField(unique=True, db_index=True)
    name_arabic = models.CharField(max_length=100)
    name_uz = models.CharField(max_length=100)
    name_english = models.CharField(max_length=100, blank=True)
    revelation_place = models.CharField(max_length=50, default='makkah')
    total_ayahs = models.PositiveIntegerField()

    class Meta:
        ordering = ['number']

    def __str__(self):
        return f"{self.number}. {self.name_uz} ({self.name_arabic})"

class Ayah(models.Model):
    surah = models.ForeignKey(Surah, related_name='ayahs', on_delete=models.CASCADE)
    number_in_surah = models.PositiveIntegerField()
    number_global = models.PositiveIntegerField(unique=True, null=True, blank=True)
    text_arabic_tajweed = models.TextField(help_text="Uthmanic script with Tajweed diacritics")
    text_arabic_clean = models.TextField(help_text="Clean text without diacritics for search")
    text_translit = models.TextField(blank=True, default='', help_text="Latin transliteration")
    text_translation_uz = models.TextField(blank=True, default='', help_text="Uzbek translation")
    official_audio_url = models.URLField(max_length=500, blank=True, default='')

    class Meta:
        ordering = ['surah', 'number_in_surah']
        unique_together = ('surah', 'number_in_surah')

    def __str__(self):
        return f"Surah {self.surah.number}:{self.number_in_surah}"

class RecitationAttempt(models.Model):
    user = models.ForeignKey(TelegramUser, related_name='attempts', on_delete=models.CASCADE, null=True, blank=True)
    ayah = models.ForeignKey(Ayah, related_name='attempts', on_delete=models.CASCADE)
    audio_file = models.FileField(upload_to='recitations/%Y/%m/%d/', null=True, blank=True)
    score = models.IntegerField(default=0, help_text="Accuracy score (0-100)")
    word_level_result = models.JSONField(default=list, help_text="Word by word evaluation array")
    overall_feedback = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Attempt by {self.user} on {self.ayah} - Score: {self.score}%"

class UserProgress(models.Model):
    STATUS_CHOICES = (
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    )
    user = models.ForeignKey(TelegramUser, related_name='progress', on_delete=models.CASCADE)
    surah = models.ForeignKey(Surah, on_delete=models.CASCADE)
    ayah = models.ForeignKey(Ayah, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')
    attempts_count = models.PositiveIntegerField(default=1)
    best_score = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'ayah')
        ordering = ['surah', 'ayah']

    def __str__(self):
        return f"{self.user} - {self.ayah} ({self.status} / {self.best_score}%)"


class BroadcastMessage(models.Model):
    TARGET_CHOICES = (
        ('all', 'Barcha foydalanuvchilar'),
        ('active', 'Faol qorilar (kamida 1 tilovat qilganlar)'),
        ('inactive', 'Hali tilovat topshirmaganlar'),
    )

    STATUS_CHOICES = (
        ('draft', 'Qoralama (Yuborilmagan)'),
        ('sending', 'Yuborilmoqda...'),
        ('sent', 'Muvaffaqiyatli yuborildi'),
        ('failed', 'Xatolik bilan tugadi'),
    )

    title = models.CharField(max_length=255, help_text="Xabarnoma ichki nomi (admin uchun)")
    message_text = models.TextField(help_text="Xabar matni (HTML formatida: <b>qalin</b>, <i>kursiv</i>, {name} shaxsiy ism)")
    photo = models.FileField(upload_to='broadcasts/%Y/%m/', null=True, blank=True, help_text="Xabarga qo'shiladigan rasm (ixtiyoriy)")
    button_text = models.CharField(max_length=100, blank=True, default='', help_text="Inline tugma yozuvi (masalan: 📖 Tilovatni Boshlash)")
    button_url = models.URLField(max_length=500, blank=True, default='', help_text="Tugma bosilganda ochiladigan havola")
    target_audience = models.CharField(max_length=20, choices=TARGET_CHOICES, default='all', help_text="Xabar kimlarga yetkazilsin?")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    sent_count = models.PositiveIntegerField(default=0, help_text="Yetkazilganlar soni")
    failed_count = models.PositiveIntegerField(default=0, help_text="Yetib bormaganlar soni")
    error_summary = models.TextField(blank=True, default='', help_text="Xatolik tafsilotlari")
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Ommaviy Xabarnoma"
        verbose_name_plural = "Ommaviy Xabarnomalar"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} [{self.get_status_display()}]"

