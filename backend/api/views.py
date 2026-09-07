import os
import sys
import logging
import requests
from django.conf import settings
from rest_framework import status, views
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from .models import TelegramUser, Surah, Ayah, RecitationAttempt, UserProgress
from .serializers import (
    SurahSerializer, AyahSerializer, RecitationAttemptSerializer,
    UserProgressSerializer, TelegramUserSerializer
)

# Import local alignment fallback if ASR service is remote or offline
try:
    from asr_service.alignment import align_words, compute_overall_score
except ImportError:
    # Add root directory to sys.path
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
    if root_dir not in sys.path:
        sys.path.insert(0, root_dir)
    from asr_service.alignment import align_words, compute_overall_score

logger = logging.getLogger(__name__)

class SurahListView(views.APIView):
    def get(self, request):
        telegram_id = request.query_params.get('telegram_id')
        surahs = Surah.objects.all().order_by('number')
        serializer = SurahSerializer(surahs, many=True, context={'telegram_id': telegram_id})
        return Response(serializer.data)

class SurahDetailView(views.APIView):
    def get(self, request, number):
        telegram_id = request.query_params.get('telegram_id')
        try:
            surah = Surah.objects.get(number=number)
        except Surah.DoesNotExist:
            return Response({'error': 'Surah topilmadi'}, status=status.HTTP_404_NOT_FOUND)
        serializer = SurahSerializer(surah, context={'telegram_id': telegram_id})
        return Response(serializer.data)

class AyahListView(views.APIView):
    def get(self, request, number):
        telegram_id = request.query_params.get('telegram_id')
        ayahs = Ayah.objects.filter(surah__number=number).order_by('number_in_surah')
        serializer = AyahSerializer(ayahs, many=True, context={'telegram_id': telegram_id})
        return Response(serializer.data)

class AyahDetailView(views.APIView):
    def get(self, request, id):
        telegram_id = request.query_params.get('telegram_id')
        try:
            ayah = Ayah.objects.get(id=id)
        except Ayah.DoesNotExist:
            return Response({'error': 'Oyat topilmadi'}, status=status.HTTP_404_NOT_FOUND)
        serializer = AyahSerializer(ayah, context={'telegram_id': telegram_id})
        return Response(serializer.data)

class RecitationCheckView(views.APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request):
        ayah_id = request.data.get('ayah_id')
        telegram_id = request.data.get('telegram_id')
        audio_file = request.FILES.get('audio_file')
        spoken_text = request.data.get('spoken_text')

        if not ayah_id:
            return Response({'error': 'ayah_id talab qilinadi'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            ayah = Ayah.objects.get(id=ayah_id)
        except Ayah.DoesNotExist:
            return Response({'error': 'Oyat topilmadi'}, status=status.HTTP_404_NOT_FOUND)

        expected_text = ayah.text_arabic_tajweed or ayah.text_arabic_clean
        eval_result = None

        # 1. Attempt evaluation via FastAPI ASR microservice
        asr_url = f"{settings.ASR_SERVICE_URL}/evaluate-recitation"
        try:
            files = None
            data = {'expected_text': expected_text}
            if audio_file:
                audio_file.seek(0)
                files = {'audio_file': (audio_file.name, audio_file.read(), audio_file.content_type)}
            elif spoken_text:
                data['spoken_text'] = spoken_text

            resp = requests.post(asr_url, data=data, files=files, timeout=12)
            if resp.status_code == 200:
                eval_result = resp.json()
        except Exception as e:
            logger.warning(f"ASR microservice unreachable ({e}). Using internal alignment fallback.")

        # 2. Resilient Internal Fallback if ASR service did not reply
        if not eval_result:
            expected_words = expected_text.strip().split()

            # If no spoken_text was captured, try audio speech recognition
            if not spoken_text and audio_file:
                try:
                    import speech_recognition as sr
                    recognizer = sr.Recognizer()
                    audio_file.seek(0)
                    with sr.AudioFile(audio_file) as src:
                        audio_data = recognizer.record(src)
                        spoken_text = recognizer.recognize_google(audio_data, language='ar-SA')
                except Exception:
                    pass

            if spoken_text and spoken_text.strip():
                spoken_words = spoken_text.strip().split()
                aligned = align_words(expected_words, spoken_words)
                summary = compute_overall_score(aligned)
            else:
                # User did not speak, audio was silent, or recognition returned empty
                aligned = [
                    {
                        'index': i,
                        'word': w,
                        'word_clean': w,
                        'spoken': None,
                        'similarity': 0.0,
                        'status': 'missing',
                        'tajweed_issues': [{'rule': 'omission', 'message_uz': "Ushbu so'z o'qilmadi"}],
                        'rules_present': []
                    }
                    for i, w in enumerate(expected_words)
                ]
                summary = {
                    'score': 0,
                    'correct_count': 0,
                    'tajweed_issue_count': 0,
                    'incorrect_count': len(expected_words),
                    'total_words': len(expected_words),
                    'feedback': "Ovozdan hech qanday qiroat yoki arabcha so'z aniqlanmadi. Iltimos, mikrofonga yaqinroq bo'lib, ovoz chiqarib tilovat qiling."
                }

            eval_result = {
                'score': summary['score'],
                'correct_count': summary['correct_count'],
                'tajweed_issue_count': summary['tajweed_issue_count'],
                'incorrect_count': summary['incorrect_count'],
                'total_words': summary['total_words'],
                'overall_feedback': summary['feedback'],
                'aligned_words': aligned,
                'engine': 'phonetic-alignment'
            }

        score = eval_result.get('score', 0)
        passed = (score >= 70)

        # 3. Handle User and Progress Record
        user = None
        if telegram_id:
            user, _ = TelegramUser.objects.get_or_create(telegram_id=telegram_id)

        # Save recitation attempt
        attempt = RecitationAttempt.objects.create(
            user=user,
            ayah=ayah,
            audio_file=audio_file,
            score=score,
            word_level_result=eval_result.get('aligned_words', []),
            overall_feedback=eval_result.get('overall_feedback', '')
        )

        # Update UserProgress
        if user:
            progress, _ = UserProgress.objects.get_or_create(
                user=user,
                surah=ayah.surah,
                ayah=ayah
            )
            progress.attempts_count += 1
            if score > progress.best_score:
                progress.best_score = score
            if passed:
                progress.status = 'completed'
            progress.save()

            # Update current pointers
            user.current_surah_number = ayah.surah.number
            user.current_ayah_number = ayah.number_in_surah
            user.save()

        # Find next ayah
        next_ayah = Ayah.objects.filter(
            surah=ayah.surah,
            number_in_surah=ayah.number_in_surah + 1
        ).first()

        return Response({
            'success': True,
            'attempt_id': attempt.id,
            'score': score,
            'passed': passed,
            'word_results': eval_result.get('aligned_words', []),
            'overall_feedback': eval_result.get('overall_feedback', ''),
            'correct_count': eval_result.get('correct_count', 0),
            'tajweed_issue_count': eval_result.get('tajweed_issue_count', 0),
            'incorrect_count': eval_result.get('incorrect_count', 0),
            'total_words': eval_result.get('total_words', 0),
            'next_ayah_id': next_ayah.id if next_ayah else None,
            'next_ayah_number': next_ayah.number_in_surah if next_ayah else None,
            'has_next_ayah': (next_ayah is not None)
        })

class UserRegisterView(views.APIView):
    def post(self, request):
        telegram_id = request.data.get('telegram_id')
        if not telegram_id:
            return Response({'error': 'telegram_id talab qilinadi'}, status=status.HTTP_400_BAD_REQUEST)

        user, created = TelegramUser.objects.get_or_create(
            telegram_id=telegram_id,
            defaults={
                'username': request.data.get('username'),
                'first_name': request.data.get('first_name', ''),
                'last_name': request.data.get('last_name', '')
            }
        )
        if not created:
            user.username = request.data.get('username', user.username)
            user.first_name = request.data.get('first_name', user.first_name)
            user.last_name = request.data.get('last_name', user.last_name)
            user.save()

        serializer = TelegramUserSerializer(user)
        return Response({'success': True, 'user': serializer.data, 'created': created})

class UserProgressView(views.APIView):
    def get(self, request):
        telegram_id = request.query_params.get('telegram_id')
        if not telegram_id:
            return Response({'error': 'telegram_id parametrini bering'}, status=status.HTTP_400_BAD_REQUEST)

        user = TelegramUser.objects.filter(telegram_id=telegram_id).first()
        if not user:
            return Response({'completed_ayahs': 0, 'total_attempts': 0, 'avg_score': 0})

        progress_items = UserProgress.objects.filter(user=user)
        completed_count = progress_items.filter(status='completed').count()
        attempts = RecitationAttempt.objects.filter(user=user)
        total_attempts = attempts.count()
        avg_score = 0
        if total_attempts > 0:
            scores = [a.score for a in attempts]
            avg_score = int(sum(scores) / len(scores))

        return Response({
            'telegram_id': user.telegram_id,
            'current_surah': user.current_surah_number,
            'current_ayah': user.current_ayah_number,
            'completed_ayahs': completed_count,
            'total_attempts': total_attempts,
            'average_score': avg_score
        })
