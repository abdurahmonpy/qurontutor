from django import template
from django.db.models import Avg, Count
from api.models import TelegramUser, RecitationAttempt, Surah, BroadcastMessage

register = template.Library()

@register.simple_tag
def get_dashboard_kpis():
    try:
        total_users = TelegramUser.objects.count()
        total_attempts = RecitationAttempt.objects.count()
        avg_score = RecitationAttempt.objects.aggregate(Avg('score'))['score__avg'] or 0
        total_broadcasts = BroadcastMessage.objects.count()
        total_surahs = Surah.objects.count()
        excellent_count = RecitationAttempt.objects.filter(score__gte=85).count()

        return {
            'total_users': total_users,
            'total_attempts': total_attempts,
            'avg_score': round(float(avg_score), 1),
            'total_broadcasts': total_broadcasts,
            'total_surahs': total_surahs,
            'excellent_count': excellent_count,
        }
    except Exception as e:
        return {
            'total_users': 0,
            'total_attempts': 0,
            'avg_score': 0,
            'total_broadcasts': 0,
            'total_surahs': 0,
            'excellent_count': 0,
        }
