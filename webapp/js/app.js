/**
 * Master Application Controller for Learn Quran (Iqra Tutor)
 */
(function () {
  const API_BASE = window.location.origin.includes(':8000') || window.location.origin.includes(':5173')
    ? `${window.location.origin}/api`
    : 'http://127.0.0.1:8000/api';

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

  // Application State
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

  // DOM Elements - Views
  const viewSurahs = document.getElementById('viewSurahs');
  const viewPractice = document.getElementById('viewPractice');

  // DOM Elements - Surahs Screen
  const surahSearchInput = document.getElementById('surahSearchInput');
  const surahsListContainer = document.getElementById('surahsListContainer');
  const overallProgressText = document.getElementById('overallProgressText');
  const overallProgressRing = document.getElementById('overallProgressRing');

  // DOM Elements - Practice Screen Header
  const btnClosePractice = document.getElementById('btnClosePractice');
  const practiceProgressBar = document.getElementById('practiceProgressBar');
  const practiceAyahCounter = document.getElementById('practiceAyahCounter');
  const btnInfoTajweed = document.getElementById('btnInfoTajweed');
  const practiceSurahName = document.getElementById('practiceSurahName');
  const practiceSurahArabic = document.getElementById('practiceSurahArabic');

  // DOM Elements - Ayah Card
  const cardAyahBadge = document.getElementById('cardAyahBadge');
  const btnPlayOfficialAudio = document.getElementById('btnPlayOfficialAudio');
  const playAudioIcon = document.getElementById('playAudioIcon');
  const audioPlayingAnimation = document.getElementById('audioPlayingAnimation');
  const officialAudioElement = document.getElementById('officialAudioElement');
  const quranTextContainer = document.getElementById('quranTextContainer');
  const translitContainer = document.getElementById('translitContainer');
  const translationContainer = document.getElementById('translationContainer');
  const liveTranscriptBox = document.getElementById('liveTranscriptBox');
  const liveTranscriptText = document.getElementById('liveTranscriptText');

  // DOM Elements - Evaluation Banner
  const evaluationResultCard = document.getElementById('evaluationResultCard');
  const resultScoreBadge = document.getElementById('resultScoreBadge');
  const resultScorePercent = document.getElementById('resultScorePercent');
  const resultFeedbackTitle = document.getElementById('resultFeedbackTitle');
  const resultFeedbackText = document.getElementById('resultFeedbackText');
  const btnRetryRecitation = document.getElementById('btnRetryRecitation');
  const btnProceedNextAyah = document.getElementById('btnProceedNextAyah');

  // DOM Elements - Controls
  const controlsIdle = document.getElementById('controlsIdle');
  const controlsRecording = document.getElementById('controlsRecording');
  const btnPrevAyah = document.getElementById('btnPrevAyah');
  const btnNextAyah = document.getElementById('btnNextAyah');
  const btnRecord = document.getElementById('btnRecord');
  const btnStopRecord = document.getElementById('btnStopRecord');
  const btnCancelRecord = document.getElementById('btnCancelRecord');
  const recordingTimer = document.getElementById('recordingTimer');

  // DOM Elements - Modals & Tabs
  const tajweedInfoModal = document.getElementById('tajweedInfoModal');
  const btnCloseInfoModal = document.getElementById('btnCloseInfoModal');
  const wordDetailsModal = document.getElementById('wordDetailsModal');
  const btnCloseWordModal = document.getElementById('btnCloseWordModal');
  const modalArabicWord = document.getElementById('modalArabicWord');
  const modalWordStatus = document.getElementById('modalWordStatus');
  const modalWordIssues = document.getElementById('modalWordIssues');
  const navTabJourney = document.getElementById('navTabJourney');
  const navTabQuran = document.getElementById('navTabQuran');

  // Format English verse title (e.g. "Al-Faatiha")
  function formatEnglishName(surah) {
    if (!surah) return '';
    const nameMap = {
      1: 'Al-Faatiha',
      2: 'Al-Baqara',
      3: 'Aal-i-Imraan',
      4: 'An-Nisaa',
      5: 'Al-Maaida',
      6: "Al-An'aam",
      7: "Al-A'raaf",
      108: 'Al-Kawthar',
      112: 'Al-Ikhlaas',
      113: 'Al-Falaq',
      114: 'An-Naas'
    };
    return nameMap[surah.number] || surah.name_simple || surah.name_uz || `Surah ${surah.number}`;
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
    // View switching via Close Button
    btnClosePractice.addEventListener('click', () => {
      stopAudioPlayback();
      if (state.isRecording) cancelRecording();
      showSurahsView();
    });

    // Bottom Navigation Tabs
    if (navTabJourney) {
      navTabJourney.addEventListener('click', () => {
        stopAudioPlayback();
        showSurahsView();
      });
    }

    if (navTabQuran) {
      navTabQuran.addEventListener('click', () => {
        if (state.currentSurah) {
          showPracticeView();
        } else if (state.surahs.length > 0) {
          selectSurah(state.surahs[0]);
        }
      });
    }

    // Search filter
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

    // Info Modal
    btnInfoTajweed.addEventListener('click', () => tajweedInfoModal.classList.remove('hidden'));
    btnCloseInfoModal.addEventListener('click', () => tajweedInfoModal.classList.add('hidden'));
    tajweedInfoModal.addEventListener('click', (e) => {
      if (e.target === tajweedInfoModal) tajweedInfoModal.classList.add('hidden');
    });

    // Word Details Modal
    btnCloseWordModal.addEventListener('click', () => wordDetailsModal.classList.add('hidden'));
    wordDetailsModal.addEventListener('click', (e) => {
      if (e.target === wordDetailsModal) wordDetailsModal.classList.add('hidden');
    });

    // Ayah Navigation
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

    // Official Audio Playback
    btnPlayOfficialAudio.addEventListener('click', toggleOfficialAudio);
    officialAudioElement.addEventListener('ended', onOfficialAudioEnded);

    // Recording Controls
    btnRecord.addEventListener('click', startRecording);
    btnStopRecord.addEventListener('click', finishAndCheckRecitation);
    btnCancelRecord.addEventListener('click', cancelRecording);

    // Evaluation Banner Buttons
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
        alert('Tabriklaymiz! Siz ushbu suraning barcha oyatlarini yakunladingiz!');
        showSurahsView();
      }
    });
  }

  // ==========================================
  // VIEW SWITCHING
  // ==========================================
  function showSurahsView() {
    viewPractice.classList.add('hidden');
    viewSurahs.classList.remove('hidden');
    window.scrollTo({ top: 0, behavior: 'smooth' });

    if (navTabJourney && navTabQuran) {
      navTabJourney.classList.add('text-[#D97706]', 'font-extrabold');
      navTabJourney.classList.remove('text-zinc-400');
      navTabQuran.classList.remove('text-[#D97706]', 'font-extrabold');
      navTabQuran.classList.add('text-zinc-400');
    }
  }

  function showPracticeView() {
    viewSurahs.classList.add('hidden');
    viewPractice.classList.remove('hidden');
    window.scrollTo({ top: 0, behavior: 'smooth' });

    if (navTabJourney && navTabQuran) {
      navTabQuran.classList.add('text-[#D97706]', 'font-extrabold');
      navTabQuran.classList.remove('text-zinc-400');
      navTabJourney.classList.remove('text-[#D97706]', 'font-extrabold');
      navTabJourney.classList.add('text-zinc-400');
    }
  }

  // ==========================================
  // DATA FETCHING & RENDERING
  // ==========================================
  async function loadSurahs() {
    try {
      const res = await fetch(`${API_BASE}/surahs/?telegram_id=${telegramId}`);
      if (!res.ok) throw new Error('Suralarni yuklab boʻlmadi');
      const data = await res.json();
      state.surahs = data;
      renderSurahsList(state.surahs);

      // Select first surah by default
      if (state.surahs.length > 0 && !state.currentSurah) {
        state.currentSurah = state.surahs[0];
      }
    } catch (e) {
      surahsListContainer.innerHTML = `
        <div class="p-4 bg-red-50 text-red-700 text-xs rounded-2xl border border-red-200 text-center">
          Tarmoq xatosi: ${e.message}. Iltimos, qayta urinib ko'ring.
        </div>`;
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
      const verseCount = surah.ayah_count || (surah.number === 1 ? 7 : 10);

      card.innerHTML = `
        <div class="flex items-center gap-3.5">
          <!-- Circular Number Badge with dot -->
          <div class="surah-num-badge shrink-0">
            ${surah.number}
          </div>

          <!-- Surah Title & Verses -->
          <div>
            <h3 class="font-bold text-zinc-900 text-[15px] leading-tight">${enName}</h3>
            <p class="text-xs text-zinc-400 font-medium mt-0.5">${verseCount} verses</p>
          </div>
        </div>

        <!-- Arabic Name -->
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
    practiceSurahName.textContent = formatEnglishName(surah);
    practiceSurahArabic.textContent = surah.name_arabic || '';

    showPracticeView();
    await loadAyahsForSurah(surah.id);
  }

  async function loadAyahsForSurah(surahId) {
    quranTextContainer.innerHTML = '<span class="text-zinc-400 text-sm font-sans animate-pulse">Oyatlar yuklanmoqda...</span>';
    translitContainer.textContent = '...';
    translationContainer.textContent = '...';

    try {
      const res = await fetch(`${API_BASE}/surahs/${surahId}/ayahs/?telegram_id=${telegramId}`);
      if (!res.ok) throw new Error('Oyatlar yuklanmadi');
      const data = await res.json();
      state.ayahs = data;

      if (state.ayahs.length > 0) {
        displayCurrentAyah();
      } else {
        quranTextContainer.textContent = "Ushbu surada oyat ma'lumotlari topilmadi.";
      }
    } catch (e) {
      quranTextContainer.innerHTML = `<span class="text-red-500 text-xs font-sans">Xatolik: ${e.message}</span>`;
    }
  }

  function displayCurrentAyah() {
    stopAudioPlayback();
    if (state.isRecording) cancelRecording();

    const ayah = state.ayahs[state.currentAyahIndex];
    if (!ayah) return;

    // Reset Evaluation Banner
    evaluationResultCard.classList.add('hidden');
    liveTranscriptBox.classList.add('hidden');
    showIdleControls();

    // Update Counter & Progress
    const totalAyahs = state.ayahs.length;
    const currentNum = state.currentAyahIndex + 1;
    practiceAyahCounter.textContent = `${currentNum}/${totalAyahs}`;
    cardAyahBadge.textContent = `Ayah: ${ayah.ayah_number}`;

    const progressPercent = Math.round((currentNum / totalAyahs) * 100);
    practiceProgressBar.style.width = `${progressPercent}%`;

    // Render Quran Text with Uthmanic font
    if (window.TajweedHighlighter) {
      window.TajweedHighlighter.renderDefaultAyah(
        ayah.text_arabic_tajweed || ayah.text_arabic_clean,
        quranTextContainer,
        ayah.ayah_number
      );
    } else {
      quranTextContainer.textContent = ayah.text_arabic_clean || ayah.text_arabic_tajweed;
    }

    // Transliteration & Translation
    translitContainer.textContent = ayah.transliteration || 'Transliteratsiya mavjud emas';
    translationContainer.textContent = ayah.translation_uz || ayah.translation_en || "Tarjima mavjud emas";

    // Setup Official Audio
    if (ayah.audio_url) {
      officialAudioElement.src = ayah.audio_url;
      btnPlayOfficialAudio.classList.remove('opacity-50', 'pointer-events-none');
    } else {
      officialAudioElement.removeAttribute('src');
      btnPlayOfficialAudio.classList.add('opacity-50', 'pointer-events-none');
    }

    // Prev / Next button states
    btnPrevAyah.classList.toggle('opacity-30', state.currentAyahIndex === 0);
    btnPrevAyah.classList.toggle('pointer-events-none', state.currentAyahIndex === 0);

    btnNextAyah.classList.toggle('opacity-30', state.currentAyahIndex === totalAyahs - 1);
    btnNextAyah.classList.toggle('pointer-events-none', state.currentAyahIndex === totalAyahs - 1);
  }

  // ==========================================
  // OFFICIAL AUDIO PLAYBACK
  // ==========================================
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

  // ==========================================
  // RECORDING & EVALUATION
  // ==========================================
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
      state.audioRecorder.stop();
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
        spokenText = recResult.spokenText || state.audioRecorder.transcript || '';
      } catch (e) {
        console.warn('Audio stop error:', e);
      }
    }

    state.isRecording = false;

    // Send to backend for verification
    await submitRecitationForCheck(audioBlob, spokenText);
  }

  async function submitRecitationForCheck(audioBlob, spokenText) {
    const ayah = state.ayahs[state.currentAyahIndex];
    if (!ayah) return;

    // Visual loading state
    quranTextContainer.innerHTML = '<span class="text-amber-600 text-sm font-sans animate-pulse">Tilovat tekshirilmoqda...</span>';

    const formData = new FormData();
    formData.append('ayah_id', ayah.id);
    formData.append('telegram_id', telegramId);

    if (spokenText) {
      formData.append('spoken_text', spokenText);
    }
    if (audioBlob) {
      formData.append('audio_file', audioBlob, 'recitation.webm');
    }

    try {
      const res = await fetch(`${API_BASE}/recitations/check/`, {
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

    // 1. Highlight Words in Quran Text Card
    if (result.aligned_words && window.TajweedHighlighter) {
      window.TajweedHighlighter.renderWords(
        result.aligned_words,
        quranTextContainer,
        (wordData) => openWordModal(wordData),
        ayah.ayah_number
      );
    }

    // 2. Render Score and Feedback Banner
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

    // Update Overall Progress Ring if score is good
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

  // Boot on DOM ready
  document.addEventListener('DOMContentLoaded', init);
})();