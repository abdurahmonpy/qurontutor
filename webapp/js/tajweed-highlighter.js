/**
 * Professional Tajweed Highlighter & Calligraphic Word Renderer
 */
class TajweedHighlighter {
  static arabicNumeral(n) {
    const arabicDigits = ['٠', '١', '٢', '٣', '٤', '٥', '٦', '٧', '٨', '٩'];
    return String(n).split('').map((d) => arabicDigits[parseInt(d, 10)] || d).join('');
  }

  static renderWords(alignedWords, containerElement, onWordClick, ayahNumber = 1) {
    if (!containerElement) return;
    containerElement.innerHTML = '';

    alignedWords.forEach((item, index) => {
      const span = document.createElement('span');
      const status = item.status || 'correct';
      span.className = `word-pill word-${status} quran-word`;
      span.textContent = item.word;
      span.dataset.index = index;

      // Status indicator badge on hover/touch
      span.addEventListener('click', () => {
        if (onWordClick) {
          onWordClick(item);
        }
      });

      containerElement.appendChild(span);
    });

    // Append ornate Calligraphic Ayah End Symbol (۝) with Arabic numeral
    const ayahEnd = document.createElement('span');
    ayahEnd.className = 'ayah-end-symbol';
    ayahEnd.innerHTML = `۝${this.arabicNumeral(ayahNumber)}`;
    containerElement.appendChild(ayahEnd);
  }

  static renderDefaultAyah(arabicText, containerElement, ayahNumber = 1) {
    if (!containerElement) return;
    containerElement.innerHTML = '';

    const words = (arabicText || '').trim().split(/\s+/);
    words.forEach((word) => {
      const span = document.createElement('span');
      span.className = 'word-pill hover:bg-white/10 text-amber-100 transition-all cursor-default';
      span.textContent = word;
      containerElement.appendChild(span);
    });

    const ayahEnd = document.createElement('span');
    ayahEnd.className = 'ayah-end-symbol';
    ayahEnd.innerHTML = `۝${this.arabicNumeral(ayahNumber)}`;
    containerElement.appendChild(ayahEnd);
  }
}

window.TajweedHighlighter = TajweedHighlighter;
