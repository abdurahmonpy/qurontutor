/**
 * Master Application Controller for Learn Quran (Iqra Tutor)
 */
(function () {
  // Relative API URL - always points to the current server (Railway, local, or custom domain)
  const API_BASE = '/api';

  // Default Fatiha ayahs fallback for offline resiliency
  const DEFAULT_FATIHA_AYAHS = [
    {
      id: 1,
      number_in_surah: 1,
      ayah_number: 1,
      text_arabic_tajweed: 'بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ',
      text_arabic_clean: 'بسم الله الرحمن الرحيم',
      text_translit: 'Bismillahir Rohmanir Rohiym',
      transliteration: 'Bismillahir Rohmanir Rohiym',
      text_translation_uz: 'Mehribon va rahmli Allohning nomi ila boshlayman.',
      translation_uz: 'Mehribon va rahmli Allohning nomi ila boshlayman.',
      official_audio_url: 'https://everyayah.com/data/Alafasy_128kbps/001001.mp3',
      audio_url: 'https://everyayah.com/data/Alafasy_128kbps/001001.mp3'
    },
    {
      id: 2,
      number_in_surah: 2,
      ayah_number: 2,
      text_arabic_tajweed: 'ٱلْحَمْدُ لِلَّهِ رَبِّ ٱلْعَٰلَمِينَ',
      text_arabic_clean: 'الحمد لله رب العالمين',
      text_translit: "Alhamdu lillahi Robbil 'alamiyn",
      transliteration: "Alhamdu lillahi Robbil 'alamiyn",
      text_translation_uz: 'Hamd butun olamlar Parvardigori Allohgadir.',
      translation_uz: 'Hamd butun olamlar Parvardigori Allohgadir.',
      official_audio_url: 'https://everyayah.com/data/Alafasy_128kbps/001002.mp3',
      audio_url: 'https://everyayah.com/data/Alafasy_128kbps/001002.mp3'
    },
    {
      id: 3,
      number_in_surah: 3,
      ayah_number: 3,
      text_arabic_tajweed: 'ٱلرَّحْمَٰنِ ٱلرَّحِيمِ',
      text_arabic_clean: 'الرحمن الرحيم',
      text_translit: 'Ar-Rohmanir-Rohiym',
      transliteration: 'Ar-Rohmanir-Rohiym',
      text_translation_uz: 'U Mehribon va Rahmlidir.',
      translation_uz: 'U Mehribon va Rahmlidir.',
      official_audio_url: 'https://everyayah.com/data/Alafasy_128kbps/001003.mp3',
      audio_url: 'https://everyayah.com/data/Alafasy_128kbps/001003.mp3'
    },
    {
      id: 4,
      number_in_surah: 4,
      ayah_number: 4,
      text_arabic_tajweed: 'مَٰلِكِ يَوْمِ ٱلدِّينِ',
      text_arabic_clean: 'مالك يوم الدين',
      text_translit: 'Maliki yavmid-diyn',
      transliteration: 'Maliki yavmid-diyn',
      text_translation_uz: 'Qiyomat kunining Egasidir.',
      translation_uz: 'Qiyomat kunining Egasidir.',
      official_audio_url: 'https://everyayah.com/data/Alafasy_128kbps/001004.mp3',
      audio_url: 'https://everyayah.com/data/Alafasy_128kbps/001004.mp3'
    },
    {
      id: 5,
      number_in_surah: 5,
      ayah_number: 5,
      text_arabic_tajweed: 'إِيَّاكَ نَعْبُدُ وَإِيَّاكَ نَسْتَعِينُ',
      text_arabic_clean: 'إياك نعبد وإياك نستعين',
      text_translit: "Iyyaka na'budu va iyyaka nasta'iyn",
      transliteration: "Iyyaka na'budu va iyyaka nasta'iyn",
      text_translation_uz: "Faqat Sengagina ibodat qilamiz va faqat Sendangina yordam so'raymiz.",
      translation_uz: "Faqat Sengagina ibodat qilamiz va faqat Sendangina yordam so'raymiz.",
      official_audio_url: 'https://everyayah.com/data/Alafasy_128kbps/001005.mp3',
      audio_url: 'https://everyayah.com/data/Alafasy_128kbps/001005.mp3'
    },
    {
      id: 6,
      number_in_surah: 6,
      ayah_number: 6,
      text_arabic_tajweed: 'ٱهْدِنَا ٱلصِّرَٰطَ ٱلْمُسْتَقِيمَ',
      text_arabic_clean: 'اهدنا الصراط المستقيم',
      text_translit: 'Ihdinas-sirotol-mustaqiym',
      transliteration: 'Ihdinas-sirotol-mustaqiym',
      text_translation_uz: "Bizni to'g'ri yo'lga hidoyat qilgin.",
      translation_uz: "Bizni to'g'ri yo'lga hidoyat qilgin.",
      official_audio_url: 'https://everyayah.com/data/Alafasy_128kbps/001006.mp3',
      audio_url: 'https://everyayah.com/data/Alafasy_128kbps/001006.mp3'
    },
    {
      id: 7,
      number_in_surah: 7,
      ayah_number: 7,
      text_arabic_tajweed: 'صِرَٰطَ ٱلَّذِينَ أَنْعَمْتَ عَلَيْهِمْ غَيْرِ ٱلْمَغْضُوبِ عَلَيْهِمْ وَلَا ٱلضَّآلِّينَ',
      text_arabic_clean: 'صراط الذين أنعمت عليهم غير المغضوب عليهم ولا الضالين',
      text_translit: "Sirotollaziyna an'amta 'alayhim g'oyril mag'dubi 'alayhim valad-doolliyn",
      transliteration: "Sirotollaziyna an'amta 'alayhim g'oyril mag'dubi 'alayhim valad-doolliyn",
      text_translation_uz: "O'zing ne'mat berganlarning yo'liga, g'azabga uchraganlarnikiga emas va zalolatga ketganlarnikiga ham emas.",
      translation_uz: "O'zing ne'mat berganlarning yo'liga, g'azabga uchraganlarnikiga emas va zalolatga ketganlarnikiga ham emas.",
      official_audio_url: 'https://everyayah.com/data/Alafasy_128kbps/001007.mp3',
      audio_url: 'https://everyayah.com/data/Alafasy_128kbps/001007.mp3'
    }
  ];

  const BACKUP_SURAHS = [
    { id: 1, number: 1, name_uz: 'Fotiha', name_arabic: 'الفاتحة', ayah_count: 7 },
    { id: 112, number: 112, name_uz: 'Ixlos', name_arabic: 'الإخلاص', ayah_count: 4 },
    { id: 113, number: 113, name_uz: 'Falaq', name_arabic: 'الفلق', ayah_count: 5 },
    { id: 114, number: 114, name_uz: 'Nos', name_arabic: 'الناس', ayah_count: 6 },
    { id: 108, number: 108, name_uz: 'Kavsar', name_arabic: 'الكوثر', ayah_count: 3 }
  ];

  // Telegram WebApp Setup
  const tg = window.Telegram?.WebApp;
  let telegramUser = null;
  if (tg) {
    tg.ready();
    tg.expand();
    telegramUser = tg.initDataUnsafe?.user;
  }

  const urlParams = new URLSearchParams(window.location.search);
  const telegramId = telegramUser?.id || urlParams.get('tg_id') || 1001;

  // State
  let state = {
    surahs: [],
    currentSurah: null,
    ayahs: [],
    currentAyahIndex: 0,
    isRecording: false,
    audioRecorder: null,
    isPlayingAudio: false,
    timerInterval: null,
    recordSeconds: 0
  };

  // DOM Elements
  const viewSurahs = document.getElementById('viewSurahs');
  const viewPractice = document.getElementById('viewPractice');

  const surahSearchInput = document.getElementById('surahSearchInput');
  const surahsListContainer = document.getElementById('surahsListContainer');
  const overallProgressText = document.getElementById('overallProgressText');
  const overallProgressRing = document.getElementById('overallProgressRing');

  const btnClosePractice = document.getElementById('btnClosePractice');
  const practiceProgressBar = document.getElementById('practiceProgressBar');
  const practiceAyahCounter = document.getElementById('practiceAyahCounter');
  const btnInfoTajweed = document.getElementById('btnInfoTajweed');
  const practiceSurahName = document.getElementById('practiceSurahName');
  const practiceSurahArabic = document.getElementById('practiceSurahArabic');

  const RECITERS = {
    husary_muallim: {
      name: 'Mahmud Xalil al-Xusoriy (Muallim)',
      getUrl: (s, a) => `https://everyayah.com/data/Husary_Muallim_128kbps/${String(s).padStart(3, '0')}${String(a).padStart(3, '0')}.mp3`
    },
    husary: {
      name: 'Mahmud Xalil al-Xusoriy (Murattal)',
      getUrl: (s, a) => `https://everyayah.com/data/Husary_128kbps/${String(s).padStart(3, '0')}${String(a).padStart(3, '0')}.mp3`
    },
    alafasy: {
      name: 'Mishariy Roshid al-Afasiy',
      getUrl: (s, a) => `https://everyayah.com/data/Alafasy_128kbps/${String(s).padStart(3, '0')}${String(a).padStart(3, '0')}.mp3`
    },
    abdulbasit: {
      name: 'Abdulbosit Abdussamad (Murattal)',
      getUrl: (s, a) => `https://everyayah.com/data/Abdul_Basit_Murattal_192kbps/${String(s).padStart(3, '0')}${String(a).padStart(3, '0')}.mp3`
    }
  };

  const cardAyahBadge = document.getElementById('cardAyahBadge');
  const reciterSelect = document.getElementById('reciterSelect');
  const btnPlayOfficialAudio = document.getElementById('btnPlayOfficialAudio');
  const playAudioIcon = document.getElementById('playAudioIcon');
  const audioPlayingAnimation = document.getElementById('audioPlayingAnimation');
  const officialAudioElement = document.getElementById('officialAudioElement');
  const quranTextContainer = document.getElementById('quranTextContainer');
  const translitContainer = document.getElementById('translitContainer');
  const translationContainer = document.getElementById('translationContainer');
  const liveTranscriptBox = document.getElementById('liveTranscriptBox');
  const liveTranscriptText = document.getElementById('liveTranscriptText');

  const evaluationResultCard = document.getElementById('evaluationResultCard');
  const resultScoreBadge = document.getElementById('resultScoreBadge');
  const resultScorePercent = document.getElementById('resultScorePercent');
  const resultFeedbackTitle = document.getElementById('resultFeedbackTitle');
  const resultFeedbackText = document.getElementById('resultFeedbackText');
  const btnRetryRecitation = document.getElementById('btnRetryRecitation');
  const btnProceedNextAyah = document.getElementById('btnProceedNextAyah');

  const controlsIdle = document.getElementById('controlsIdle');
  const controlsRecording = document.getElementById('controlsRecording');
  const btnPrevAyah = document.getElementById('btnPrevAyah');
  const btnNextAyah = document.getElementById('btnNextAyah');
  const btnRecord = document.getElementById('btnRecord');
  const btnStopRecord = document.getElementById('btnStopRecord');
  const btnCancelRecord = document.getElementById('btnCancelRecord');
  const recordingTimer = document.getElementById('recordingTimer');

  const tajweedInfoModal = document.getElementById('tajweedInfoModal');
  const btnCloseInfoModal = document.getElementById('btnCloseInfoModal');
  const wordDetailsModal = document.getElementById('wordDetailsModal');
  const btnCloseWordModal = document.getElementById('btnCloseWordModal');
  const modalArabicWord = document.getElementById('modalArabicWord');
  const modalWordStatus = document.getElementById('modalWordStatus');
  const modalWordIssues = document.getElementById('modalWordIssues');

  function formatEnglishName(surah) {
    if (!surah) return '';
    const nameMap = {
      1: 'Fotiha',
      2: 'Baqara',
      3: 'Oli Imron',
      4: 'Niso',
      5: 'Moida',
      108: 'Kavsar',
      112: 'Ixlos',
      113: 'Falaq',
      114: 'Nos'
    };
    return nameMap[surah.number] || surah.name_uz || surah.name_english || surah.name_simple || `Sura ${surah.number}`;
  }

  async function init() {
    setupEventListeners();
    setupAudioRecorder();
    await loadSurahs();
  }

  function setupAudioRecorder() {
    if (!window.QuranAudioRecorder) return;
    
    state.audioRecorder = new window.QuranAudioRecorder({
      onStateChange: (recState) => {
        if (recState.status === 'error') {
          alert(`Ovoz yozishda xatolik: ${recState.error}`);
          stopRecordingTimer();
          showIdleControls();
        }
      }
    });

    state.audioRecorder.onTranscript = (text) => {
      if (text && liveTranscriptBox && liveTranscriptText) {
        liveTranscriptBox.classList.remove('hidden');
        liveTranscriptText.textContent = text;
      }
    };
  }

  function setupEventListeners() {
    btnClosePractice.addEventListener('click', () => {
      stopAudioPlayback();
      if (state.isRecording) cancelRecording();
      showSurahsView();
    });

    surahSearchInput.addEventListener('input', (e) => {
      const q = e.target.value.toLowerCase().trim();
      const filtered = state.surahs.filter((s) => {
        const enName = formatEnglishName(s).toLowerCase();
        const uzName = (s.name_uz || '').toLowerCase();
        const arName = (s.name_arabic || '');
        const numStr = s.number.toString();
        return enName.includes(q) || uzName.includes(q) || arName.includes(q) || numStr === q;
      });
      renderSurahsList(filtered);
    });

    btnInfoTajweed.addEventListener('click', () => tajweedInfoModal.classList.remove('hidden'));
    btnCloseInfoModal.addEventListener('click', () => tajweedInfoModal.classList.add('hidden'));
    tajweedInfoModal.addEventListener('click', (e) => {
      if (e.target === tajweedInfoModal) tajweedInfoModal.classList.add('hidden');
    });

    btnCloseWordModal.addEventListener('click', () => wordDetailsModal.classList.add('hidden'));
    wordDetailsModal.addEventListener('click', (e) => {
      if (e.target === wordDetailsModal) wordDetailsModal.classList.add('hidden');
    });

    btnPrevAyah.addEventListener('click', () => {
      if (state.currentAyahIndex > 0) {
        state.currentAyahIndex--;
        displayCurrentAyah();
      }
    });

    btnNextAyah.addEventListener('click', () => {
      if (state.currentAyahIndex < state.ayahs.length - 1) {
        state.currentAyahIndex++;
        displayCurrentAyah();
      }
    });

    if (reciterSelect) {
      const savedReciter = localStorage.getItem('quran_tutor_reciter') || 'husary_muallim';
      reciterSelect.value = savedReciter;

      reciterSelect.addEventListener('change', (e) => {
        localStorage.setItem('quran_tutor_reciter', e.target.value);
        const wasPlaying = state.isPlayingAudio;
        stopAudioPlayback();
        updateReciterAudioSource();
        if (wasPlaying) {
          toggleOfficialAudio();
        }
      });
    }

    btnPlayOfficialAudio.addEventListener('click', toggleOfficialAudio);
    officialAudioElement.addEventListener('ended', onOfficialAudioEnded);

    btnRecord.addEventListener('click', startRecording);
    btnStopRecord.addEventListener('click', finishAndCheckRecitation);
    btnCancelRecord.addEventListener('click', cancelRecording);

    btnRetryRecitation.addEventListener('click', () => {
      evaluationResultCard.classList.add('hidden');
      displayCurrentAyah();
    });

    btnProceedNextAyah.addEventListener('click', () => {
      evaluationResultCard.classList.add('hidden');
      if (state.currentAyahIndex < state.ayahs.length - 1) {
        state.currentAyahIndex++;
        displayCurrentAyah();
      } else {
        alert('Mashalloh! Siz ushbu suraning barcha oyatlarini yakunladingiz!');
        showSurahsView();
      }
    });
  }

  function showSurahsView() {
    viewPractice.classList.add('hidden');
    viewSurahs.classList.remove('hidden');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  function showPracticeView() {
    viewSurahs.classList.add('hidden');
    viewPractice.classList.remove('hidden');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  async function loadSurahs() {
    try {
      const res = await fetch(`${API_BASE}/surahs/?telegram_id=${telegramId}`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();

      if (Array.isArray(data) && data.length > 0) {
        state.surahs = data;
      } else {
        state.surahs = BACKUP_SURAHS;
      }
      renderSurahsList(state.surahs);

      if (state.surahs.length > 0 && !state.currentSurah) {
        state.currentSurah = state.surahs[0];
      }
    } catch (e) {
      console.warn('API error, using backup surahs:', e);
      state.surahs = BACKUP_SURAHS;
      renderSurahsList(state.surahs);
    }
  }

  function renderSurahsList(surahs) {
    if (!surahs || surahs.length === 0) {
      surahsListContainer.innerHTML = `
        <div class="py-12 text-center text-zinc-400 text-xs">
          Hech qanday sura topilmadi
        </div>`;
      return;
    }

    surahsListContainer.innerHTML = '';

    surahs.forEach((surah) => {
      const card = document.createElement('div');
      card.className = 'flex items-center justify-between p-3.5 bg-white rounded-2xl border border-zinc-100 shadow-sm hover:border-amber-400/80 hover:shadow-md transition-all cursor-pointer transform active:scale-[0.99]';
      
      const enName = formatEnglishName(surah);
      const verseCount = surah.ayah_count || surah.total_ayahs || (surah.number === 1 ? 7 : 4);

      card.innerHTML = `
        <div class="flex items-center gap-3.5">
          <div class="surah-num-badge shrink-0">
            ${surah.number}
          </div>
          <div>
            <h3 class="font-bold text-zinc-900 text-[15px] leading-tight">${enName} surasi</h3>
            <p class="text-xs text-zinc-400 font-medium mt-0.5">${verseCount} oyat</p>
          </div>
        </div>
        <div class="arabic-font text-xl font-bold text-zinc-800 shrink-0">
          ${surah.name_arabic || ''}
        </div>
      `;

      card.addEventListener('click', () => {
        selectSurah(surah);
      });

      surahsListContainer.appendChild(card);
    });
  }

  async function selectSurah(surah) {
    state.currentSurah = surah;
    state.currentAyahIndex = 0;
    practiceSurahName.textContent = `${formatEnglishName(surah)} surasi`;
    practiceSurahArabic.textContent = surah.name_arabic || '';

    showPracticeView();
    await loadAyahsForSurah(surah);
  }

  async function loadAyahsForSurah(surah) {
    const surahNum = surah.number || surah.id || 1;
    quranTextContainer.innerHTML = '<span class="text-zinc-400 text-sm font-sans animate-pulse">Oyatlar yuklanmoqda...</span>';
    translitContainer.textContent = '...';
    translationContainer.textContent = '...';

    try {
      const res = await fetch(`${API_BASE}/surahs/${surahNum}/ayahs/?telegram_id=${telegramId}`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();

      if (Array.isArray(data) && data.length > 0) {
        state.ayahs = data;
      } else {
        state.ayahs = surahNum === 1 ? DEFAULT_FATIHA_AYAHS : [];
      }

      if (state.ayahs.length > 0) {
        displayCurrentAyah();
      } else {
        quranTextContainer.textContent = "Oyat ma'lumotlari topilmadi.";
      }
    } catch (e) {
      console.warn('Ayah fetch failed, using default:', e);
      state.ayahs = surahNum === 1 ? DEFAULT_FATIHA_AYAHS : [];
      if (state.ayahs.length > 0) {
        displayCurrentAyah();
      } else {
        quranTextContainer.innerHTML = `<span class="text-red-500 text-xs font-sans">Oyatni yuklab bo'lmadi (${e.message})</span>`;
      }
    }
  }

  function getReciterAudioUrl(ayah) {
    if (!ayah) return '';
    const selected = localStorage.getItem('quran_tutor_reciter') || (reciterSelect ? reciterSelect.value : 'husary_muallim');
    const reciterConfig = RECITERS[selected] || RECITERS.husary_muallim;

    if (ayah.reciters_audio && ayah.reciters_audio[selected]) {
      return ayah.reciters_audio[selected];
    }

    const surahNum = state.currentSurah?.number || state.currentSurah?.id || 1;
    const ayahNum = ayah.ayah_number || ayah.number_in_surah || (state.currentAyahIndex + 1);
    return reciterConfig.getUrl(surahNum, ayahNum);
  }

  function updateReciterAudioSource() {
    const ayah = state.ayahs[state.currentAyahIndex];
    if (!ayah) return;
    const audioSrc = getReciterAudioUrl(ayah);
    if (audioSrc) {
      officialAudioElement.src = audioSrc;
      btnPlayOfficialAudio.classList.remove('opacity-50', 'pointer-events-none');
    } else {
      officialAudioElement.removeAttribute('src');
      btnPlayOfficialAudio.classList.add('opacity-50', 'pointer-events-none');
    }
  }

  function displayCurrentAyah() {
    stopAudioPlayback();
    if (state.isRecording) cancelRecording();

    const ayah = state.ayahs[state.currentAyahIndex];
    if (!ayah) return;

    evaluationResultCard.classList.add('hidden');
    liveTranscriptBox.classList.add('hidden');
    showIdleControls();

    const totalAyahs = state.ayahs.length;
    const currentNum = state.currentAyahIndex + 1;
    const ayahNum = ayah.ayah_number || ayah.number_in_surah || currentNum;

    practiceAyahCounter.textContent = `${currentNum}/${totalAyahs}`;
    cardAyahBadge.textContent = `${ayahNum}-oyat`;

    const progressPercent = Math.round((currentNum / totalAyahs) * 100);
    practiceProgressBar.style.width = `${progressPercent}%`;

    // Render Quran Text with Uthmanic font and Harakat
    const arabicText = ayah.text_arabic_tajweed || ayah.text_arabic_clean || '';
    if (window.TajweedHighlighter) {
      window.TajweedHighlighter.renderDefaultAyah(
        arabicText,
        quranTextContainer,
        ayahNum
      );
    } else {
      quranTextContainer.textContent = arabicText;
    }

    // Transliteration & Translation
    translitContainer.textContent = ayah.transliteration || ayah.text_translit || "Bismillahir Rohmanir Rohiym";
    translationContainer.textContent = ayah.translation_uz || ayah.text_translation_uz || ayah.translation_en || "Mehribon va rahmli Allohning nomi ila boshlayman.";

    // Setup Selected Reciter Audio
    updateReciterAudioSource();

    btnPrevAyah.classList.toggle('opacity-30', state.currentAyahIndex === 0);
    btnPrevAyah.classList.toggle('pointer-events-none', state.currentAyahIndex === 0);

    btnNextAyah.classList.toggle('opacity-30', state.currentAyahIndex === totalAyahs - 1);
    btnNextAyah.classList.toggle('pointer-events-none', state.currentAyahIndex === totalAyahs - 1);
  }

  function toggleOfficialAudio() {
    if (state.isPlayingAudio) {
      stopAudioPlayback();
    } else {
      if (!officialAudioElement.src) return;
      officialAudioElement.play().then(() => {
        state.isPlayingAudio = true;
        playAudioIcon.classList.add('hidden');
        audioPlayingAnimation.classList.remove('hidden');
        btnPlayOfficialAudio.classList.add('ring-2', 'ring-amber-400');
      }).catch((err) => {
        console.warn('Audio play failed:', err);
      });
    }
  }

  function stopAudioPlayback() {
    officialAudioElement.pause();
    officialAudioElement.currentTime = 0;
    state.isPlayingAudio = false;
    playAudioIcon.classList.remove('hidden');
    audioPlayingAnimation.classList.add('hidden');
    btnPlayOfficialAudio.classList.remove('ring-2', 'ring-amber-400');
  }

  function onOfficialAudioEnded() {
    state.isPlayingAudio = false;
    playAudioIcon.classList.remove('hidden');
    audioPlayingAnimation.classList.add('hidden');
    btnPlayOfficialAudio.classList.remove('ring-2', 'ring-amber-400');
  }

  async function startRecording() {
    stopAudioPlayback();
    evaluationResultCard.classList.add('hidden');

    try {
      if (state.audioRecorder) {
        await state.audioRecorder.start();
      }
      state.isRecording = true;
      state.recordSeconds = 0;
      recordingTimer.textContent = '0s';

      showRecordingControls();
      startRecordingTimer();
    } catch (e) {
      alert(`Mikrofonni yoqib boʻlmadi: ${e.message}`);
      showIdleControls();
    }
  }

  function startRecordingTimer() {
    stopRecordingTimer();
    state.timerInterval = setInterval(() => {
      state.recordSeconds++;
      recordingTimer.textContent = `${state.recordSeconds}s`;
    }, 1000);
  }

  function stopRecordingTimer() {
    if (state.timerInterval) {
      clearInterval(state.timerInterval);
      state.timerInterval = null;
    }
  }

  function cancelRecording() {
    stopRecordingTimer();
    if (state.audioRecorder) {
      state.audioRecorder.cancel();
    }
    state.isRecording = false;
    liveTranscriptBox.classList.add('hidden');
    showIdleControls();
  }

  async function finishAndCheckRecitation() {
    stopRecordingTimer();
    showIdleControls();

    let audioBlob = null;
    let spokenText = '';

    if (state.audioRecorder) {
      try {
        const recResult = await state.audioRecorder.stop();
        audioBlob = recResult.audioBlob || recResult.blob;
        spokenText = recResult.spokenText || state.audioRecorder.spokenTranscript || '';
      } catch (e) {
        console.warn('Audio stop error:', e);
      }
    }

    state.isRecording = false;

    await submitRecitationForCheck(audioBlob, spokenText);
  }

  async function submitRecitationForCheck(audioBlob, spokenText) {
    const ayah = state.ayahs[state.currentAyahIndex];
    if (!ayah) return;

    quranTextContainer.innerHTML = '<span class="text-amber-600 text-sm font-sans animate-pulse">Tilovat tekshirilmoqda...</span>';

    const formData = new FormData();
    const ayahId = ayah.id || ayah.number_in_surah || (state.currentAyahIndex + 1);
    formData.append('ayah_id', ayahId);
    formData.append('telegram_id', telegramId);

    if (spokenText) {
      formData.append('spoken_text', spokenText);
    }
    if (audioBlob) {
      formData.append('audio_file', audioBlob, 'recitation.webm');
    }

    try {
      // Use resilient check endpoint
      const res = await fetch(`${API_BASE}/recitation/check/`, {
        method: 'POST',
        body: formData
      });

      if (!res.ok) throw new Error(`Server xatosi (${res.status})`);
      const result = await res.json();
      renderEvaluationResult(result, ayah);
    } catch (e) {
      displayCurrentAyah();
      alert(`Tekshirishda xatolik yuz berdi: ${e.message}`);
    }
  }

  function renderEvaluationResult(result, ayah) {
    const score = Math.round(result.score || 0);

    if (result.aligned_words && window.TajweedHighlighter) {
      window.TajweedHighlighter.renderWords(
        result.aligned_words,
        quranTextContainer,
        (wordData) => openWordModal(wordData),
        ayah.ayah_number || ayah.number_in_surah || 1
      );
    }

    resultScorePercent.textContent = `${score}%`;
    evaluationResultCard.classList.remove('hidden');

    if (score >= 85) {
      resultScoreBadge.className = 'px-2.5 py-1 rounded-xl text-xs font-extrabold bg-emerald-100 text-emerald-700';
      resultFeedbackTitle.textContent = "Mashalloh! A'lo tilovat!";
      resultFeedbackTitle.className = 'text-xs font-bold text-emerald-700';
      evaluationResultCard.className = 'app-card p-4 mb-4 border-l-4 border-emerald-500 transition-all';
      if (window.confetti) {
        window.confetti({ particleCount: 50, spread: 60, origin: { y: 0.7 } });
      }
    } else if (score >= 60) {
      resultScoreBadge.className = 'px-2.5 py-1 rounded-xl text-xs font-extrabold bg-amber-100 text-amber-700';
      resultFeedbackTitle.textContent = "Yaxshi, tajvidga e'tibor bering";
      resultFeedbackTitle.className = 'text-xs font-bold text-amber-700';
      evaluationResultCard.className = 'app-card p-4 mb-4 border-l-4 border-amber-500 transition-all';
    } else {
      resultScoreBadge.className = 'px-2.5 py-1 rounded-xl text-xs font-extrabold bg-red-100 text-red-700';
      resultFeedbackTitle.textContent = "Qayta o'qib ko'ring";
      resultFeedbackTitle.className = 'text-xs font-bold text-red-700';
      evaluationResultCard.className = 'app-card p-4 mb-4 border-l-4 border-red-500 transition-all';
    }

    resultFeedbackText.textContent = result.feedback || "Tilovat natijalari tayyor bo'ldi.";

    if (score >= 70 && overallProgressRing && overallProgressText) {
      const completed = state.currentAyahIndex + 1;
      const pct = Math.round((completed / state.ayahs.length) * 100);
      overallProgressText.textContent = `${pct}%`;
      overallProgressRing.setAttribute('stroke-dasharray', `${pct}, 100`);
    }
  }

  function openWordModal(wordData) {
    modalArabicWord.textContent = wordData.word || '';
    modalWordIssues.innerHTML = '';

    const statusMap = {
      correct: { text: "To'g'ri o'qilgan", cls: 'bg-emerald-100 text-emerald-700' },
      tajweed_issue: { text: 'Tajvid qoidasi', cls: 'bg-amber-100 text-amber-700' },
      incorrect: { text: 'Xato oʻqilgan', cls: 'bg-red-100 text-red-700' },
      missing: { text: "O'qilmay qoldirilgan", cls: 'bg-red-100 text-red-700' }
    };

    const st = statusMap[wordData.status] || statusMap.correct;
    modalWordStatus.textContent = st.text;
    modalWordStatus.className = `mt-2 text-xs font-bold px-2.5 py-1 rounded-full inline-block ${st.cls}`;

    if (wordData.tajweed_issues && wordData.tajweed_issues.length > 0) {
      wordData.tajweed_issues.forEach((iss) => {
        const item = document.createElement('div');
        item.className = 'p-2 rounded-xl bg-zinc-50 border border-zinc-100 text-xs text-zinc-700';
        item.textContent = iss.message_uz || iss.rule || 'Tajvid qoidasi';
        modalWordIssues.appendChild(item);
      });
    } else {
      const item = document.createElement('div');
      item.className = 'p-2 text-xs text-zinc-400 text-center';
      item.textContent = 'Ushbu soʻzda tajvid kamchiligi aniqlanmadi.';
      modalWordIssues.appendChild(item);
    }

    wordDetailsModal.classList.remove('hidden');
  }

  function showIdleControls() {
    controlsRecording.classList.add('hidden');
    controlsIdle.classList.remove('hidden');
  }

  function showRecordingControls() {
    controlsIdle.classList.add('hidden');
    controlsRecording.classList.remove('hidden');
  }

  document.addEventListener('DOMContentLoaded', init);
})();