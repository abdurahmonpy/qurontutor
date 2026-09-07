"""
Management command to seed or fetch Quranic Surahs and Ayahs.
Usage:
  python manage.py import_quran --sample       (Seeds Al-Fatiha, Al-Ikhlas, Al-Falaq, An-Nas, Al-Kawthar)
  python manage.py import_quran --surah 1      (Fetches Surah 1 from Quran.com API)
  python manage.py import_quran --juz-amma     (Fetches Surahs 78 to 114)
"""
import requests
from django.core.management.base import BaseCommand
from api.models import Surah, Ayah

# Bundled High-Quality Seed Data (Always works offline without external network dependency)
SAMPLE_SURAHS = [
    {
        'number': 1,
        'name_arabic': 'الفاتحة',
        'name_uz': 'Fotiha',
        'name_english': 'Al-Faatiha',
        'revelation_place': 'makkah',
        'total_ayahs': 7,
        'ayahs': [
            {
                'num': 1,
                'tajweed': 'بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ',
                'clean': 'بسم الله الرحمن الرحيم',
                'translit': "Bismillahir Rohmanir Rohiym",
                'uz': "Mehribon va rahmli Allohning nomi ila boshlayman.",
                'audio': 'https://everyayah.com/data/Alafasy_128kbps/001001.mp3'
            },
            {
                'num': 2,
                'tajweed': 'ٱلْحَمْدُ لِلَّهِ رَبِّ ٱلْعَٰلَمِينَ',
                'clean': 'الحمد لله رب العالمين',
                'translit': "Alhamdu lillahi Robbil 'alamiyn",
                'uz': "Hamd butun olamlar Parvardigori Allohgadir.",
                'audio': 'https://everyayah.com/data/Alafasy_128kbps/001002.mp3'
            },
            {
                'num': 3,
                'tajweed': 'ٱلرَّحْمَٰنِ ٱلرَّحِيمِ',
                'clean': 'الرحمن الرحيم',
                'translit': "Ar-Rohmanir-Rohiym",
                'uz': "U Mehribon va Rahmlidir.",
                'audio': 'https://everyayah.com/data/Alafasy_128kbps/001003.mp3'
            },
            {
                'num': 4,
                'tajweed': 'مَٰلِكِ يَوْمِ ٱلدِّينِ',
                'clean': 'مالك يوم الدين',
                'translit': "Maliki yavmid-diyn",
                'uz': "Qiyomat kunining Egasidir.",
                'audio': 'https://everyayah.com/data/Alafasy_128kbps/001004.mp3'
            },
            {
                'num': 5,
                'tajweed': 'إِيَّاكَ نَعْبُدُ وَإِيَّاكَ نَسْتَعِينُ',
                'clean': 'إياك نعبد وإياك نستعين',
                'translit': "Iyyaka na'budu va iyyaka nasta'iyn",
                'uz': "Faqat Sengagina ibodat qilamiz va faqat Sendangina yordam so'raymiz.",
                'audio': 'https://everyayah.com/data/Alafasy_128kbps/001005.mp3'
            },
            {
                'num': 6,
                'tajweed': 'ٱهْدِنَا ٱلصِّرَٰطَ ٱلْمُسْتَقِيمَ',
                'clean': 'اهدنا الصراط المستقيم',
                'translit': "Ihdinas-sirotol mustaqiym",
                'uz': "Bizni to'g'ri yo'lga hidoyat qilgin.",
                'audio': 'https://everyayah.com/data/Alafasy_128kbps/001006.mp3'
            },
            {
                'num': 7,
                'tajweed': 'صِرَٰطَ ٱلَّذِينَ أَنْعَمْتَ عَلَيْهِمْ غَيْرِ ٱلْمَغْضُوبِ عَلَيْهِمْ وَلَا ٱلضَّآلِّينَ',
                'clean': 'صراط الذين أنعمت عليهم غير المغضوب عليهم ولا الضالين',
                'translit': "Sirotollaziyna an'amta 'alayhim g'oyril mag'dubi 'alayhim valad-doolliyn",
                'uz': "O'zing ne'mat berganlarning yo'liga, g'azabga uchraganlarning va adashganlarning yo'liga emas.",
                'audio': 'https://everyayah.com/data/Alafasy_128kbps/001007.mp3'
            }
        ]
    },
    {
        'number': 112,
        'name_arabic': 'الإخلاص',
        'name_uz': 'Ixlos',
        'name_english': 'Al-Ikhlaas',
        'revelation_place': 'makkah',
        'total_ayahs': 4,
        'ayahs': [
            {
                'num': 1,
                'tajweed': 'قُلْ هُوَ ٱللَّهُ أَحَدٌ',
                'clean': 'قل هو الله أحد',
                'translit': "Qul huvallohu ahad",
                'uz': "Ayt: «U Alloh Yagonadir».",
                'audio': 'https://everyayah.com/data/Alafasy_128kbps/112001.mp3'
            },
            {
                'num': 2,
                'tajweed': 'ٱللَّهُ ٱلصَّمَدُ',
                'clean': 'الله الصمد',
                'translit': "Allohus-somad",
                'uz': "«Alloh Samaddir (hech kimga muhtoj emas, barcha Unga muhtojdir)».",
                'audio': 'https://everyayah.com/data/Alafasy_128kbps/112002.mp3'
            },
            {
                'num': 3,
                'tajweed': 'لَمْ يَلِدْ وَلَمْ يُولَدْ',
                'clean': 'لم يلد ولم يولد',
                'translit': "Lam yalid va lam yuvlad",
                'uz': "«U tug'magan va tug'ilmagandir».",
                'audio': 'https://everyayah.com/data/Alafasy_128kbps/112003.mp3'
            },
            {
                'num': 4,
                'tajweed': 'وَلَمْ يَكُن لَّهُۥ كُفُوًا أَحَدٌۢ',
                'clean': 'ولم يكن له كفوا أحد',
                'translit': "Va lam yakul-lahu kufuvan ahad",
                'uz': "«Va hech kim Unga teng bo'la olmas».",
                'audio': 'https://everyayah.com/data/Alafasy_128kbps/112004.mp3'
            }
        ]
    },
    {
        'number': 113,
        'name_arabic': 'الفلق',
        'name_uz': 'Falaq',
        'name_english': 'Al-Falaq',
        'revelation_place': 'makkah',
        'total_ayahs': 5,
        'ayahs': [
            {
                'num': 1,
                'tajweed': 'قُلْ أَعُوذُ بِرَبِّ ٱلْفَلَقِ',
                'clean': 'قل أعوذ برب الفلق',
                'translit': "Qul a'uzu birobbil falaq",
                'uz': "Ayt: «Tong Robbidan panoh so'rayman».",
                'audio': 'https://everyayah.com/data/Alafasy_128kbps/113001.mp3'
            },
            {
                'num': 2,
                'tajweed': 'مِن شَرِّ مَا خَلَقَ',
                'clean': 'من شر ما خلق',
                'translit': "Min sharri ma xolaq",
                'uz': "«U yaratgan narsalarning yomonligidan».",
                'audio': 'https://everyayah.com/data/Alafasy_128kbps/113002.mp3'
            },
            {
                'num': 3,
                'tajweed': 'وَمِن شَرِّ غَاسِقٍ إِذَا وَقَبَ',
                'clean': 'ومن شر غاسق إذا وقب',
                'translit': "Va min sharri g'osiqin iza vaqob",
                'uz': "«Zulmatga cho'mgan tun yomonligidan».",
                'audio': 'https://everyayah.com/data/Alafasy_128kbps/113003.mp3'
            },
            {
                'num': 4,
                'tajweed': 'وَمِن شَرِّ ٱلنَّفَّٰثَٰتِ فِى ٱلْعُقَدِ',
                'clean': 'ومن شر النفاثات في العقد',
                'translit': "Va min sharrin-naffaasaati fiyl 'uqod",
                'uz': "«Tugunlarga dam soluvchi ayollar yomonligidan».",
                'audio': 'https://everyayah.com/data/Alafasy_128kbps/113004.mp3'
            },
            {
                'num': 5,
                'tajweed': 'وَمِن شَرِّ حَاسِدٍ إِذَا حَسَدَ',
                'clean': 'ومن شر حاسد إذا حسد',
                'translit': "Va min sharri haasidin iza hasad",
                'uz': "«Va hasad qilayotgan hasadchining yomonligidan».",
                'audio': 'https://everyayah.com/data/Alafasy_128kbps/113005.mp3'
            }
        ]
    },
    {
        'number': 114,
        'name_arabic': 'الناس',
        'name_uz': 'Nos',
        'name_english': 'An-Naas',
        'revelation_place': 'makkah',
        'total_ayahs': 6,
        'ayahs': [
            {
                'num': 1,
                'tajweed': 'قُلْ أَعُوذُ بِرَبِّ ٱلنَّاسِ',
                'clean': 'قل أعوذ برب الناس',
                'translit': "Qul a'uzu birobbin-naas",
                'uz': "Ayt: «Insonlar Robbidan panoh so'rayman».",
                'audio': 'https://everyayah.com/data/Alafasy_128kbps/114001.mp3'
            },
            {
                'num': 2,
                'tajweed': 'مَلِكِ ٱلنَّاسِ',
                'clean': 'ملك الناس',
                'translit': "Malikin-naas",
                'uz': "«Insonlar Podshohidan».",
                'audio': 'https://everyayah.com/data/Alafasy_128kbps/114002.mp3'
            },
            {
                'num': 3,
                'tajweed': 'إِلَٰهِ ٱلنَّاسِ',
                'clean': 'إله الناس',
                'translit': "Ilahin-naas",
                'uz': "«Insonlar Ilohidan».",
                'audio': 'https://everyayah.com/data/Alafasy_128kbps/114003.mp3'
            },
            {
                'num': 4,
                'tajweed': 'مِن شَرِّ ٱلْوَسْوَاسِ ٱلْخَنَّاسِ',
                'clean': 'من شر الوسواس الخناس',
                'translit': "Min sharril vasvasil xonnaas",
                'uz': "«Yashirinib yuruvchi vasvasachining yomonligidan».",
                'audio': 'https://everyayah.com/data/Alafasy_128kbps/114004.mp3'
            },
            {
                'num': 5,
                'tajweed': 'ٱلَّذِى يُوَسْوِسُ فِى صُدُورِ ٱلنَّاسِ',
                'clean': 'الذي يوسوس في صدور الناس',
                'translit': "Allaziy yuvasvisu fiy sudurin-naas",
                'uz': "«Insonlarning ko'ngillariga vasvasa soladigan».",
                'audio': 'https://everyayah.com/data/Alafasy_128kbps/114005.mp3'
            },
            {
                'num': 6,
                'tajweed': 'مِنَ ٱلْجِنَّةِ وَٱلنَّاسِ',
                'clean': 'من الجنة والناس',
                'translit': "Minal jinnati van-naas",
                'uz': "«Jinlardan va insonlardan bo'lgan (shayton) yomonligidan».",
                'audio': 'https://everyayah.com/data/Alafasy_128kbps/114006.mp3'
            }
        ]
    },
    {
        'number': 108,
        'name_arabic': 'الكوثر',
        'name_uz': 'Kavsar',
        'name_english': 'Al-Kawthar',
        'revelation_place': 'makkah',
        'total_ayahs': 3,
        'ayahs': [
            {
                'num': 1,
                'tajweed': 'إِنَّآ أَعْطَيْنَٰكَ ٱلْكَوْثَرَ',
                'clean': 'إنا أعطيناك الكوثر',
                'translit': "Innaa a'toynaakal kavsar",
                'uz': "Albatta, Biz senga Kavsarni ato qildik.",
                'audio': 'https://everyayah.com/data/Alafasy_128kbps/108001.mp3'
            },
            {
                'num': 2,
                'tajweed': 'فَصَلِّ لِرَبِّكَ وَٱنْحَرْ',
                'clean': 'فصل لربك وانحر',
                'translit': "Fasolli lirobbika vanhar",
                'uz': "Bas, Robbing uchun namoz o'qi va qurbonlik so'y.",
                'audio': 'https://everyayah.com/data/Alafasy_128kbps/108002.mp3'
            },
            {
                'num': 3,
                'tajweed': 'إِنَّ شَانِئَكَ هُوَ ٱلْأَبْتَرُ',
                'clean': 'إن شانئك هو الأبتر',
                'translit': "Inna shaani'aka huval abtar",
                'uz': "Albatta, sening dushmaning – u dumi kesikdir.",
                'audio': 'https://everyayah.com/data/Alafasy_128kbps/108003.mp3'
            }
        ]
    }
]

class Command(BaseCommand):
    help = 'Seeds sample surahs or fetches surahs from Quran.com API'

    def add_arguments(self, parser):
        parser.add_argument('--sample', action='store_true', help='Seed sample short Surahs')
        parser.add_argument('--surah', type=int, help='Fetch a specific Surah number from Quran.com')
        parser.add_argument('--juz-amma', action='store_true', help='Fetch all Surahs of Juz Amma (78-114)')

    def handle(self, *args, **options):
        if options.get('surah'):
            self.fetch_surah_from_api(options['surah'])
        elif options.get('juz_amma'):
            for s_num in range(78, 115):
                self.fetch_surah_from_api(s_num)
        else:
            self.seed_sample_surahs()

    def seed_sample_surahs(self):
        self.stdout.write("Seeding sample Surahs (Fotiha, Ixlos, Falaq, Nos, Kavsar)...")
        for s_data in SAMPLE_SURAHS:
            surah, _ = Surah.objects.update_or_create(
                number=s_data['number'],
                defaults={
                    'name_arabic': s_data['name_arabic'],
                    'name_uz': s_data['name_uz'],
                    'name_english': s_data['name_english'],
                    'revelation_place': s_data['revelation_place'],
                    'total_ayahs': s_data['total_ayahs'],
                }
            )
            for a_data in s_data['ayahs']:
                Ayah.objects.update_or_create(
                    surah=surah,
                    number_in_surah=a_data['num'],
                    defaults={
                        'text_arabic_tajweed': a_data['tajweed'],
                        'text_arabic_clean': a_data['clean'],
                        'text_translit': a_data['translit'],
                        'text_translation_uz': a_data['uz'],
                        'official_audio_url': a_data['audio']
                    }
                )
            self.stdout.write(self.style.SUCCESS(f"Surah {surah.number} ({surah.name_uz}) imported successfully."))

    def fetch_surah_from_api(self, surah_number: int):
        self.stdout.write(f"Fetching Surah {surah_number} from Quran.com API...")
        try:
            # 1. Fetch chapter info
            info_url = f"https://api.quran.com/api/v4/chapters/{surah_number}"
            resp = requests.get(info_url, timeout=10)
            if resp.status_code != 200:
                self.stderr.write(f"Error fetching info for Surah {surah_number}")
                return
            ch = resp.json()['chapter']
            surah, _ = Surah.objects.update_or_create(
                number=surah_number,
                defaults={
                    'name_arabic': ch['name_arabic'],
                    'name_uz': ch['translated_name']['name'],
                    'name_english': ch['name_simple'],
                    'revelation_place': ch['revelation_place'],
                    'total_ayahs': ch['verses_count']
                }
            )

            # 2. Fetch verses
            verses_url = f"https://api.quran.com/api/v4/verses/by_chapter/{surah_number}?words=true&translations=55&audio=7&per_page=300"
            v_resp = requests.get(verses_url, timeout=15)
            if v_resp.status_code == 200:
                data = v_resp.json()
                for v in data.get('verses', []):
                    num_in_surah = v['verse_number']
                    tajweed_text = " ".join([w['text'] for w in v.get('words', []) if w.get('char_type_name') == 'word'])
                    clean_text = " ".join([w.get('text_imlaei', w['text']) for w in v.get('words', []) if w.get('char_type_name') == 'word'])
                    audio_url = f"https://verses.quran.com/{v.get('audio', {}).get('url', '')}" if v.get('audio') else ""
                    trans = v.get('translations', [{}])[0].get('text', '') if v.get('translations') else ''

                    Ayah.objects.update_or_create(
                        surah=surah,
                        number_in_surah=num_in_surah,
                        defaults={
                            'text_arabic_tajweed': tajweed_text or v.get('text_uthmani', ''),
                            'text_arabic_clean': clean_text,
                            'text_translation_uz': trans,
                            'official_audio_url': audio_url
                        }
                    )
            self.stdout.write(self.style.SUCCESS(f"Successfully fetched Surah {surah_number} ({surah.name_uz})"))
        except Exception as e:
            self.stderr.write(f"Failed to fetch Surah {surah_number}: {e}")
