from django.urls import path
from .views import (
    SurahListView, SurahDetailView, AyahListView, AyahDetailView,
    RecitationCheckView, UserRegisterView, UserProgressView
)

urlpatterns = [
    path('surahs/', SurahListView.as_view(), name='surah-list'),
    path('surahs/<int:number>/', SurahDetailView.as_view(), name='surah-detail'),
    path('surahs/<int:number>/ayahs/', AyahListView.as_view(), name='ayah-list'),
    path('ayahs/<int:id>/', AyahDetailView.as_view(), name='ayah-detail'),
    path('recitation/check/', RecitationCheckView.as_view(), name='recitation-check'),
    path('recitations/check/', RecitationCheckView.as_view(), name='recitations-check'),
    path('user/register/', UserRegisterView.as_view(), name='user-register'),
    path('user/progress/', UserProgressView.as_view(), name='user-progress'),
]
