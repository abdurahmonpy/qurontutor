"""
Forced Alignment and Phonetic String Distance for Quranic Recitation.
Maps user spoken words against the pre-known expected Ayah words.
"""
from typing import List, Dict, Any

try:
    from asr_service.tajweed_rules import normalize_arabic, evaluate_word_tajweed
except ImportError:
    from tajweed_rules import normalize_arabic, evaluate_word_tajweed

def levenshtein_similarity(s1: str, s2: str) -> float:
    """Calculates Levenshtein similarity between two Arabic strings (0.0 to 1.0)."""
    if not s1 and not s2:
        return 1.0
    if not s1 or not s2:
        return 0.0

    len1, len2 = len(s1), len(s2)
    dp = [[0] * (len2 + 1) for _ in range(len1 + 1)]

    for i in range(len1 + 1):
        dp[i][0] = i
    for j in range(len2 + 1):
        dp[0][j] = j

    for i in range(1, len1 + 1):
        for j in range(1, len2 + 1):
            cost = 0 if s1[i - 1] == s2[j - 1] else 1
            dp[i][j] = min(
                dp[i - 1][j] + 1,      # deletion
                dp[i][j - 1] + 1,      # insertion
                dp[i - 1][j - 1] + cost # substitution
            )

    dist = dp[len1][len2]
    max_len = max(len1, len2)
    return max(0.0, 1.0 - (dist / max_len))

def align_words(
    expected_words: List[str],
    spoken_words: List[str],
    durations: List[float] = None
) -> List[Dict[str, Any]]:
    """
    Performs dynamic alignment of expected Ayah words with spoken words.
    Matches closest words, flags omissions, substitutions, and Tajweed issues.
    """
    if durations is None:
        durations = [0.0] * len(spoken_words)

    norm_expected = [normalize_arabic(w) for w in expected_words]
    norm_spoken = [normalize_arabic(w) for w in spoken_words]

    aligned_results = []
    spoken_idx = 0
    num_spoken = len(norm_spoken)

    for exp_i, exp_word in enumerate(expected_words):
        exp_clean = norm_expected[exp_i]

        if spoken_idx < num_spoken:
            curr_spoken_clean = norm_spoken[spoken_idx]
            sim = levenshtein_similarity(exp_clean, curr_spoken_clean)
            
            # Check if skipping one spoken word gives a much better match
            alt_sim = 0.0
            if spoken_idx + 1 < num_spoken:
                alt_sim = levenshtein_similarity(exp_clean, norm_spoken[spoken_idx + 1])

            if alt_sim > sim and alt_sim >= 0.7:
                spoken_idx += 1
                curr_spoken_clean = norm_spoken[spoken_idx]
                sim = alt_sim

            dur = durations[spoken_idx] if spoken_idx < len(durations) else 0.0

            if sim >= 0.70:
                # Strong phonetic match
                evaluation = evaluate_word_tajweed(exp_word, spoken_words[spoken_idx], dur)
                aligned_results.append({
                    'index': exp_i,
                    'word': exp_word,
                    'word_clean': exp_clean,
                    'spoken': spoken_words[spoken_idx],
                    'similarity': round(sim * 100, 1),
                    'status': evaluation['status'],
                    'tajweed_issues': evaluation['issues'],
                    'rules_present': evaluation['rules_present']
                })
                spoken_idx += 1
            elif sim >= 0.40:
                # Partial match / Tajweed or mispronunciation
                aligned_results.append({
                    'index': exp_i,
                    'word': exp_word,
                    'word_clean': exp_clean,
                    'spoken': spoken_words[spoken_idx],
                    'similarity': round(sim * 100, 1),
                    'status': 'incorrect',
                    'tajweed_issues': [{'rule': 'pronunciation', 'message_uz': f"Talaffuz noaniq (o'xshashlik: {int(sim*100)}%)"}],
                    'rules_present': []
                })
                spoken_idx += 1
            else:
                # Word was omitted or completely different
                aligned_results.append({
                    'index': exp_i,
                    'word': exp_word,
                    'word_clean': exp_clean,
                    'spoken': None,
                    'similarity': 0.0,
                    'status': 'missing',
                    'tajweed_issues': [{'rule': 'omission', 'message_uz': "Ushbu so'z o'qilmadi yoki tushirib qoldirildi"}],
                    'rules_present': []
                })
        else:
            # Remaining words were not spoken
            aligned_results.append({
                'index': exp_i,
                'word': exp_word,
                'word_clean': exp_clean,
                'spoken': None,
                'similarity': 0.0,
                'status': 'missing',
                'tajweed_issues': [{'rule': 'omission', 'message_uz': "Ushbu so'z o'qilmadi yoki tushirib qoldirildi"}],
                'rules_present': []
            })

    return aligned_results

def compute_overall_score(aligned_words: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Computes overall accuracy percentage, correct words count, and feedback."""
    if not aligned_words:
        return {'score': 0, 'correct_count': 0, 'total': 0, 'feedback': 'Hech narsa aniqlanmadi.'}

    total = len(aligned_words)
    correct_count = 0
    tajweed_count = 0
    incorrect_count = 0

    for item in aligned_words:
        if item['status'] == 'correct':
            correct_count += 1
        elif item['status'] == 'tajweed_issue':
            tajweed_count += 1
        else:
            incorrect_count += 1

    # Weighted scoring: correct = 100%, tajweed issue = 70%, incorrect/missing = 0%
    weighted_sum = (correct_count * 1.0) + (tajweed_count * 0.75)
    score = int(round((weighted_sum / total) * 100))

    if score >= 90:
        feedback = "Mashalloh! Qiroatingiz juda a'lo darajada, barcha so'zlar deyarli mukammal o'qildi."
    elif score >= 75:
        feedback = "Yaxshi qiroat! Bir nechta tajvid yoki noaniq so'zlar bor, sariq va qizil belgilangan so'zlarga e'tibor bering."
    elif score >= 50:
        feedback = "Harakat qildingiz! Xatolar bor, rasmiy qorining qiroatini yana bir bor eshitib qayta topshiring."
    else:
        feedback = "Tilovat to'liq mos kelmadi. Iltimos, oyatni diqqat bilan takrorlab, qaytadan o'qing."

    return {
        'score': score,
        'correct_count': correct_count,
        'tajweed_issue_count': tajweed_count,
        'incorrect_count': incorrect_count,
        'total_words': total,
        'feedback': feedback
    }
