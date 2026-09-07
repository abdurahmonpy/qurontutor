"""
Tajweed Rules Verification Engine
Rule-based Arabic phonetic and Tajweed analyzer for Qur'anic recitation.
"""
import re
from typing import List, Dict, Any

# Unicode definitions for Arabic diacritics
FATHA = '\u064e'
DAMMA = '\u064f'
KASRA = '\u0650'
FATHATAN = '\u064b'
DAMMATAN = '\u064c'
KASRATAN = '\u064d'
SUKUN = '\u0652'
QURAN_SUKUN = '\u06df'
SHADDAH = '\u0651'
MADDAH = '\u0653'
SUPERSCRIPT_ALEF = '\u0670'
SMALL_HIGH_MEEM = '\u06ed'

QALQALAH_LETTERS = set('قطبجد')
IKHFA_LETTERS = set('تثجدذزسشصضطظفقك')
IDGHAM_GHUNNAH_LETTERS = set('ينمو')
IDGHAM_BILA_GHUNNAH_LETTERS = set('لر')
HALQ_LETTERS = set('ءهعحغخ')

def normalize_arabic(text: str) -> str:
    """Removes diacritics, signs and normalizes Alefs for clean text matching."""
    if not text:
        return ""
    # Strip diacritics
    text = re.sub(r'[\u064B-\u065F\u0670\u06D6-\u06ED]', '', text)
    # Normalize Alefs
    text = re.sub(r'[إأآٱ]', 'ا', text)
    # Normalize Taa Marbuta
    text = re.sub(r'ة', 'ه', text)
    # Normalize Yaa
    text = re.sub(r'ى', 'ي', text)
    return text.strip()

def extract_tajweed_features(arabic_word: str) -> List[Dict[str, Any]]:
    """
    Analyzes an Arabic word with Uthmanic diacritics and identifies Tajweed rules present in it.
    """
    rules = []
    chars = list(arabic_word)
    n = len(chars)

    for i in range(n):
        char = chars[i]
        
        # 1. Madd (Cho'ziq - 4 to 6 Harakah)
        if char == MADDAH or (char in 'اوي' and (i + 1 < n and chars[i + 1] == MADDAH)):
            rules.append({
                'rule': 'madd',
                'name': "Madd (مد)",
                'name_uz': "Madd — cho'ziq unlini 4-6 harakat cho'zish",
                'type': 'duration',
                'expected_duration_multiplier': 2.5
            })

        # 2. Ghunnah on Shaddah (Noon or Meem Mushaddadah)
        if char in 'نم' and (i + 1 < n and chars[i + 1] == SHADDAH):
            rules.append({
                'rule': 'ghunnah_shaddah',
                'name': "Ghunnah Mushaddadah (غنة مشددة)",
                'name_uz': "G'unna — Nun yoki Mim harfini 2 harakat burun orqali ushlab turish",
                'type': 'nasal',
                'letter': char
            })

        # 3. Qalqalah (Tebranish: ق، ط، ب، ج، د)
        if char in QALQALAH_LETTERS:
            has_sukun = (i + 1 < n and chars[i + 1] in [SUKUN, QURAN_SUKUN])
            is_end_of_word = (i == n - 1)
            if has_sukun or is_end_of_word:
                rules.append({
                    'rule': 'qalqalah',
                    'name': "Qalqalah (قلقلة)",
                    'name_uz': f"Qalqala — '{char}' harfida aks-sado va tebranish hosil qilish",
                    'type': 'vibration',
                    'letter': char
                })

        # 4. Iqlab (Noon Sakinah / Tanween before Baa)
        if char == SMALL_HIGH_MEEM or (char in [FATHATAN, DAMMATAN, KASRATAN] and i + 1 < n and chars[i + 1] == 'ب'):
            rules.append({
                'rule': 'iqlab',
                'name': "Iqlab (إقلاب)",
                'name_uz': "Iqlab — Nun yoki tanvinni mayin Mim tovushiga aylantirish",
                'type': 'nasal'
            })

    return rules

def evaluate_word_tajweed(expected_word: str, spoken_word: str, duration_sec: float = 0.0) -> Dict[str, Any]:
    """
    Evaluates whether the spoken word complies with expected Tajweed rules.
    Returns compliance status, feedback, and issue descriptions.
    """
    expected_clean = normalize_arabic(expected_word)
    spoken_clean = normalize_arabic(spoken_word)

    # Basic word match
    is_word_correct = (expected_clean == spoken_clean)
    rules = extract_tajweed_features(expected_word)
    
    tajweed_issues = []
    
    if is_word_correct:
        # Check rule compliance
        for r in rules:
            if r['rule'] == 'madd':
                # Madd requires sufficient vowel hold (if duration is available)
                if 0.0 < duration_sec < 0.35:
                    tajweed_issues.append({
                        'rule': r['rule'],
                        'message_uz': "Madd yetarlicha cho'zilmadi (kamida 4-6 harakat talab etiladi)",
                        'rule_name': r['name']
                    })
            elif r['rule'] == 'ghunnah_shaddah':
                # Nasalization check
                if 0.0 < duration_sec < 0.25:
                    tajweed_issues.append({
                        'rule': r['rule'],
                        'message_uz': "G'unna (burun tovushi) yetarlicha ushlab turilmadi (2 harakat)",
                        'rule_name': r['name']
                    })

    status = 'correct'
    if not is_word_correct:
        status = 'incorrect'
    elif len(tajweed_issues) > 0:
        status = 'tajweed_issue'

    return {
        'status': status,
        'rules_present': [r['name'] for r in rules],
        'issues': tajweed_issues
    }
