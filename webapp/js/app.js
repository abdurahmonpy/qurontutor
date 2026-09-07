/**
 * Master Application Controller for Iqra Quran Tutor
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

  // State
  let state = {
    surahs: [],
    currentSurah: null,
    ayahs: [],
    currentAyahIndex: 0,
    isRecording: false,
    audioRecorder: null,
    isPlayingAudio: false,
    fontSizeRem: 2.2,
    showTranslit: true,
    showTranslation: true
  };

  // DOM Elements
  const headerSurahName = document.getElementById('headerSurahName');
  const surahArabicTitle = document.getElementById('surahArabicTitle');
  const currentSurahPlace = document.getElementById('currentSurahPlace');
  const currentAyahIndicator = document.getElementById('currentAyahIndicator');
  const quranTextContainer = document.getElementById('quranTextContainer');
  const translitContainer = document.getElementById('translitContainer');
  const translationContainer = document.getElementById('translationContainer');

  const btnPrevAyah = document.getElementById('btnPrevAyah');
  const btnNextAyah = document.getElementById('btnNextAyah');

  // View toggles & font size
  const btnToggleTranslit = document.getElementById('btnToggleTranslit');
  const btnToggleTrans = document.getElementById('btnToggleTrans');
  const btnFontMinus = document.getElementById('btnFontMinus');
  const btnFontPlus = document.getElementById('btnFontPlus');

  // Official Audio
  const btnPlayOfficialAudio = document.getElementById('btnPlayOfficialAudio');
  const playAudioIcon = document.getElementById('playAudioIcon');
  const audioPlayingWave = document.getElementById('audioPlayingWave');
  const officialAudioElement = document.getElementById('officialAudioElement');
  const audioCurrentTime = document.getElementById('audioCurrentTime');
  const audioTotalDuration = document.getElementById('audioTotalDuration');
  const audioTimeline = document.getElementById('audioTimeline');

  // Record Studio
  const btnRecord = document.getElementById('btnRecord');
  const micIcon = document.getElementById('micIcon');
  const stopIcon = document.getElementById('stopIcon');
  const recordPulseRing = document.getElementById('recordPulseRing');
  const recStatusLabel = document.getElementById('recStatusLabel');
  const statusIndicatorDot = document.getElementById('statusIndicatorDot');
  const recStatusPill = document.getElementById('recStatusPill');
  const recordingTimer = document.getElementById('recordingTimer');
  const visualizerContainer = document.getElementById('visualizerContainer');
  const audioVisualizerCanvas = document.getElementById('audioVisualizerCanvas');
  const liveTranscriptBox = document.getElementById('liveTranscriptBox');
  const liveTranscriptText = document.getElementById('liveTranscriptText');

  // Evaluation & Results
  const evaluationResultCard = document.getElementById('evaluationResultCard');
  const resultScorePercent = document.getElementById('resultScorePercent');
  const resultScoreBadge = document.getElementById('resultScoreBadge');
  const scoreCirclePath = document.getElementById('scoreCirclePath');
  const statCorrectWords = document.getElementById('statCorrectWords');
  const statTajweedIssues = document.getElementById('statTajweedIssues');
  const statIncorrectWords = document.getElementById('statIncorrectWords');
  const resultFeedbackText = document.getElementById('resultFeedbackText');
  const evaluatedWordsContainer = document.getElementById('evaluatedWordsContainer');
  const btnRetryRecitation = document.getElementById('btnRetryRecitation');
  const btnProceedNextAyah = document.getElementById('btnProceedNextAyah');

  // Modals
  const btnOpenSurahs = document.getElementById('btnOpenSurahs');
  const surahsModal = document.getElementById('surahsModal');
  const btnCloseSurahsModal = document.getElementById('btnCloseSurahsModal');
  const surahSearchInput = document.getElementById('surahSearchInput');
  const surahsListContainer = document.getElementById('surahsListContainer');

  const wordDetailsModal = document.getElementById('wordDetailsModal');
  const btnCloseWordModal = document.getElementById('btnCloseWordModal');
  const modalArabicWord = document.getElementById('modalArabicWord');
  const modalWordStatus = document.getElementById('modalWordStatus');
  const modalWordIssues = document.getElementById('modalWordIssues');

  // Format MM:SS helper
  function formatTime(seconds) {
    if (isNaN(seconds) || seconds < 0) return "0:00";
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs < 10 ? '0' : ''}${secs}`;
  }

  async function init() {
    setupEventListeners();
    setupAudioRecorder();
    await loadSurahs();
  }

  function setupAudioRecorder() {
    state.audioRecorder = new window.QuranAudioRecorder({
      canvas: audioVisualizerCanvas,
      onStateChange: (recState) => {
        if (recState.status === 'recording') {
          recordingTimer.classList.remove('hidden');
          recordingTimer.textContent = formatTime(recState.duration);
        } else if (recState.status === 'idle') {
          recordingTimer.classList.add('hidden');
        } else if (recState.status === 'error') {
          alert(`Ovoz yozishda xatolik: ${recState.error}`);
          resetRecordButton();
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
    // Sura Selector
    btnOpenSurahs.addEventListener('click', () => {
      surahsModal.classList.remove('hidden');
      renderSurahsList(state.surahs);
    });
    btnCloseSurahsModal.addEventListener('click', () => surahsModal.classList.add('hidden'));

    surahSearchInput.addEventListener('input', (e) => {
      const q = e.target.value.toLowerCase().trim();
      const filtered = state.surahs.filter(
        (s) => s.name_uz.toLowerCase().includes(q) || s.name_arabic.includes(q) || s.number.toString() === q
      );
      renderSurahsList(filtered);
    });

    // Word modal
    btnCloseWordModal.addEventListener('click', () => wordDetailsModal.classList.add('hidden'));

    // Ayah navigation
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

    // Font size controls
    btnFontPlus.addEventListener('click', () => {
      if (state.fontSizeRem < 3.8) {
        state.fontSizeRem += 0.25;
        quranTextContainer.style.fontSize = `${state.fontSizeRem}rem`;
      }
    });

    btnFontMinus.addEventListener('click', () => {
      if (state.fontSizeRem > 1.6) {
        state.fontSizeRem -= 0.25;
        quranTextContainer.style.fontSize = `${state.fontSizeRem}rem`;
      }
    });

    // Transliteration & Translation toggles
    btnToggleTranslit.addEventListener('click', () => {
      state.showTranslit = !state.showTranslit;
      translitContainer.style.display = state.showTranslit ? 'block' : 'none';
      btnToggleTranslit.classList.toggle('opacity-50', !state.showTranslit);
    });

    btnToggleTrans.addEventListener('click', () => {
      state.showTranslation = !state.showTranslation;
      translationContainer.style.display = state.showTranslation ? 'block' : 'none';
      btnToggleTrans.classList.toggle('opacity-50', !state.showTranslation);
    });

    // Official Audio Playback & Timeline
    btnPlayOfficialAudio.addEventListener('click', toggleOfficialAudio);

    officialAudioElement.addEventListener('timeupdate', () => {
      const current = officialAudioElement.currentTime;
      const total = officialAudioElement.duration || 1;
      audioCurrentTime.textContent = formatTime(current);
      audioTotalDuration.textContent = formatTime(total);
      audioTimeline.value = (current / total) * 100;
    });

    audioTimeline.addEventListener('input', (e) => {
      const total = officialAudioElement.duration || 1;
      officialAudioElement.currentTime = (e.target.value / 100) * total;
    });

    officialAudioElement.addEventListener('ended', () => {
      stopOfficialAudio();
    });

    // Record toggle
    btnRecord.addEventListener('click', toggleRecording);

    // Results Actions
    btnRetryRecitation.addEventListener('click', () => {
      evaluationResultCard.classList.add('hidden');
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });

    btnProceedNextAyah.addEventListener('click', () => {
      if (state.currentAyahIndex < state.ayahs.length - 1) {
        state.currentAyahIndex++;
        displayCurrentAyah();
        evaluationResultCard.classList.add('hidden');
        window.scrollTo({ top: 0, behavior: 'smooth' });
      } else {
        alert("Mashalloh! Siz mazkur suraning barcha oyatlarini muvaffaqiyatli yakunladingiz!");
      }
    });
  }

  async function loadSurahs() {
    try {
      const res = await fetch(`${API_BASE}/surahs/?telegram_id=${telegramId}`);
      if (!res.ok) throw new Error('Suralarni yuklashda xatolik');
      state.surahs = await res.json();

      if (state.surahs.length > 0) {
        selectSurah(state.surahs[0]);
      }
    } catch (err) {
      console.error(err);
      headerSurahName.textContent = "Ulanishda xatolik";
    }
  }

  async function selectSurah(surah) {
    state.currentSurah = surah;
    state.currentAyahIndex = 0;
    headerSurahName.textContent = `${surah.number}. ${surah.name_uz}`;
    surahArabicTitle.textContent = `سورة ${surah.name_arabic}`;
    currentSurahPlace.textContent = surah.revelation_place === 'makkah' ? 'Makka' : 'Madina';
    surahsModal.classList.add('hidden');

    try {
      const res = await fetch(`${API_BASE}/surahs/${surah.number}/ayahs/?telegram_id=${telegramId}`);
      if (!res.ok) throw new Error('Oyatlarni yuklashda xatolik');
      state.ayahs = await res.json();
      displayCurrentAyah();
    } catch (err) {
      console.error(err);
    }
  }

  function displayCurrentAyah() {
    if (!state.ayahs.length) return;

    const ayah = state.ayahs[state.currentAyahIndex];
    currentAyahIndicator.textContent = `${ayah.number_in_surah} / ${state.ayahs.length} Oyat`;

    btnPrevAyah.disabled = (state.currentAyahIndex === 0);
    btnNextAyah.disabled = (state.currentAyahIndex === state.ayahs.length - 1);

    // Render Clean/Tajweed Arabic text with Ayah end symbol
    window.TajweedHighlighter.renderDefaultAyah(
      ayah.text_arabic_tajweed || ayah.text_arabic_clean,
      quranTextContainer,
      ayah.number_in_surah
    );

    // Transliteration & Translation
    translitContainer.textContent = ayah.text_translit || "—";
    translationContainer.textContent = ayah.text_translation_uz || "—";

    // Audio setup
    officialAudioElement.src = ayah.official_audio_url || '';
    stopOfficialAudio();

    // Reset evaluation card
    evaluationResultCard.classList.add('hidden');
    if (liveTranscriptBox) liveTranscriptBox.classList.add('hidden');
  }

  function toggleOfficialAudio() {
    if (!officialAudioElement.src) {
      alert("Ushbu oyat uchun audio fayl mavjud emas.");
      return;
    }

    if (state.isPlayingAudio) {
      stopOfficialAudio();
    } else {
      officialAudioElement.play();
      state.isPlayingAudio = true;
      playAudioIcon.textContent = '⏸';
      audioPlayingWave.classList.remove('hidden');
    }
  }

  function stopOfficialAudio() {
    officialAudioElement.pause();
    officialAudioElement.currentTime = 0;
    state.isPlayingAudio = false;
    playAudioIcon.textContent = '▶';
    audioPlayingWave.classList.add('hidden');
    audioTimeline.value = 0;
    audioCurrentTime.textContent = '0:00';
  }

  async function toggleRecording() {
    if (state.isRecording) {
      // STOP recording and evaluate
      state.isRecording = false;
      resetRecordButton();
      recStatusLabel.textContent = "Tilovat tahlil qilinmoqda...";

      const result = await state.audioRecorder.stop();
      const audioBlob = result?.audioBlob;
      const spokenText = result?.spokenText || '';

      await submitRecitation(audioBlob, spokenText);
    } else {
      // START recording
      stopOfficialAudio();
      if (liveTranscriptBox) liveTranscriptBox.classList.add('hidden');
      if (liveTranscriptText) liveTranscriptText.textContent = '...';

      try {
        await state.audioRecorder.start();
        state.isRecording = true;
        micIcon.classList.add('hidden');
        stopIcon.classList.remove('hidden');
        recordPulseRing.classList.remove('hidden');
        visualizerContainer.classList.remove('hidden');
        btnRecord.classList.add('is-recording');

        recStatusLabel.textContent = "Tilovat yozilmoqda... Tugatish uchun bosing";
        recStatusPill.className = "inline-flex items-center gap-2 px-3.5 py-1 rounded-full text-xs font-semibold tracking-wide bg-rose-950/60 border border-rose-500/40 text-rose-300 backdrop-blur-md";
        statusIndicatorDot.className = "w-2 h-2 rounded-full bg-rose-400 animate-ping";
      } catch (err) {
        console.error(err);
      }
    }
  }

  function resetRecordButton() {
    state.isRecording = false;
    micIcon.classList.remove('hidden');
    stopIcon.classList.add('hidden');
    recordPulseRing.classList.add('hidden');
    visualizerContainer.classList.add('hidden');
    btnRecord.classList.remove('is-recording');

    recStatusLabel.textContent = "Tilovat qilish uchun bosing";
    recStatusPill.className = "inline-flex items-center gap-2 px-3.5 py-1 rounded-full text-xs font-semibold tracking-wide bg-emerald-950/60 border border-emerald-500/40 text-emerald-300 backdrop-blur-md";
    statusIndicatorDot.className = "w-2 h-2 rounded-full bg-emerald-400 animate-pulse";
  }

  async function submitRecitation(audioBlob, spokenText = '') {
    const ayah = state.ayahs[state.currentAyahIndex];
    if (!ayah) return;

    const formData = new FormData();
    formData.append('ayah_id', ayah.id);
    formData.append('telegram_id', telegramId);
    if (audioBlob) {
      formData.append('audio_file', audioBlob, 'recitation.webm');
    }
    if (spokenText && spokenText.trim()) {
      formData.append('spoken_text', spokenText.trim());
    }

    try {
      const res = await fetch(`${API_BASE}/recitation/check/`, {
        method: 'POST',
        body: formData
      });

      if (!res.ok) throw new Error("Tilovatni tekshirishda xatolik yuz berdi");
      const result = await res.json();
      displayEvaluationResult(result, ayah.number_in_surah);
    } catch (err) {
      alert(`Xatolik: ${err.message}`);
      recStatusLabel.textContent = "Qaytadan urinib ko'ring";
    }
  }

  function displayEvaluationResult(result, ayahNumber = 1) {
    evaluationResultCard.classList.remove('hidden');
    resultScorePercent.textContent = `${result.score}%`;

    // Animate circular SVG stroke
    if (scoreCirclePath) {
      scoreCirclePath.setAttribute('stroke-dasharray', `${result.score}, 100`);
      if (result.score >= 85) {
        scoreCirclePath.setAttribute('class', 'text-emerald-400 transition-all duration-1000');
      } else if (result.score >= 70) {
        scoreCirclePath.setAttribute('class', 'text-amber-400 transition-all duration-1000');
      } else {
        scoreCirclePath.setAttribute('class', 'text-rose-400 transition-all duration-1000');
      }
    }

    // Badge styling
    if (result.score >= 85) {
      resultScoreBadge.textContent = "A'lo";
      resultScoreBadge.className = "text-xs font-bold px-3 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 shadow-sm";
      if (window.confetti) {
        window.confetti({ particleCount: 80, spread: 70, origin: { y: 0.6 } });
      }
    } else if (result.score >= 70) {
      resultScoreBadge.textContent = "Yaxshi";
      resultScoreBadge.className = "text-xs font-bold px-3 py-0.5 rounded-full bg-amber-500/20 text-amber-300 border border-amber-500/40 shadow-sm";
    } else {
      resultScoreBadge.textContent = "Qayta o'qing";
      resultScoreBadge.className = "text-xs font-bold px-3 py-0.5 rounded-full bg-rose-500/20 text-rose-300 border border-rose-500/40 shadow-sm";
    }

    statCorrectWords.textContent = result.correct_count || 0;
    statTajweedIssues.textContent = result.tajweed_issue_count || 0;
    statIncorrectWords.textContent = result.incorrect_count || 0;
    resultFeedbackText.textContent = result.overall_feedback || "Tilovat baholandi.";

    // Render word pills with ayah end marker
    window.TajweedHighlighter.renderWords(
      result.word_results || [],
      evaluatedWordsContainer,
      (wordItem) => openWordModal(wordItem),
      ayahNumber
    );

    evaluationResultCard.scrollIntoView({ behavior: 'smooth' });
  }

  function openWordModal(item) {
    modalArabicWord.textContent = item.word;

    let statusText = "To'g'ri o'qildi";
    let statusClass = "bg-emerald-500/20 text-emerald-300 border border-emerald-500/40";

    if (item.status === 'tajweed_issue') {
      statusText = "Tajvid Kamchiligi";
      statusClass = "bg-amber-500/20 text-amber-300 border border-amber-500/40";
    } else if (item.status === 'incorrect' || item.status === 'missing') {
      statusText = "Xato yoki Tushirilgan";
      statusClass = "bg-rose-500/20 text-rose-300 border border-rose-500/40";
    }

    modalWordStatus.textContent = statusText;
    modalWordStatus.className = `inline-block px-3 py-1 rounded-full text-xs font-bold uppercase mb-3 ${statusClass}`;

    modalWordIssues.innerHTML = '';

    if (item.rules_present && item.rules_present.length > 0) {
      const rulesDiv = document.createElement('div');
      rulesDiv.className = "text-[11px] text-amber-300 font-semibold mb-1.5";
      rulesDiv.textContent = `So'zdagi qoidalar: ${item.rules_present.join(', ')}`;
      modalWordIssues.appendChild(rulesDiv);
    }

    if (item.tajweed_issues && item.tajweed_issues.length > 0) {
      item.tajweed_issues.forEach((issue) => {
        const p = document.createElement('p');
        p.className = "text-rose-300";
        p.textContent = `• ${issue.message_uz || issue.rule}`;
        modalWordIssues.appendChild(p);
      });
    } else if (item.status === 'correct') {
      const p = document.createElement('p');
      p.className = "text-emerald-300";
      p.textContent = "✓ Mazkur so'z to'g'ri talaffuz qilindi.";
      modalWordIssues.appendChild(p);
    }

    wordDetailsModal.classList.remove('hidden');
  }

  function renderSurahsList(surahs) {
    surahsListContainer.innerHTML = '';

    surahs.forEach((surah) => {
      const item = document.createElement('div');
      const isCurrent = state.currentSurah && state.currentSurah.number === surah.number;
      item.className = `p-3.5 rounded-2xl border transition-all cursor-pointer flex items-center justify-between ${
        isCurrent
          ? 'bg-amber-500/15 border-amber-500/50 shadow-md shadow-amber-500/10'
          : 'bg-white/[0.03] hover:bg-emerald-950/40 border-white/10 hover:border-emerald-500/30'
      }`;

      item.innerHTML = `
        <div class="flex items-center gap-3">
          <div class="w-9 h-9 rounded-xl bg-gradient-to-tr from-amber-500/20 to-emerald-500/20 border border-amber-500/30 flex items-center justify-center font-bold text-xs text-amber-300">
            ${surah.number}
          </div>
          <div>
            <div class="font-bold text-sm text-white">${surah.name_uz}</div>
            <div class="text-[11px] text-slate-400">${surah.total_ayahs} oyat • ${surah.revelation_place === 'makkah' ? 'Makka' : 'Madina'}</div>
          </div>
        </div>
        <div class="quran-text text-xl text-amber-200">${surah.name_arabic}</div>
      `;

      item.addEventListener('click', () => selectSurah(surah));
      surahsListContainer.appendChild(item);
    });
  }

  document.addEventListener('DOMContentLoaded', init);
})();
