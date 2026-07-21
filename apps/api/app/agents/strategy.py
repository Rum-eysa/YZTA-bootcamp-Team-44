"""Ajanlar arası paylaşılan düşük-skor stratejisi (US-022 / US-050).

Önyazı ve CV özeti ajanları, eşleştirme skoru düşükse aynı "potansiyel vurgusu"
yaklaşımını kullanmalı - bu yüzden strateji seçimi tek yerde tanımlanır."""
from typing import Any

# Skor bu eşiğin altındaysa "potansiyel vurgusu" stratejisine geçilir
LOW_SCORE_THRESHOLD = 40

STRATEGY_STANDARD = (
    "Adayın ilanla eşleşen güçlü yönlerini ve somut başarılarını öne çıkar; "
    "yetkinliğini kanıtlayan örneklerle güven ver."
)
STRATEGY_POTENTIAL = (
    "Eşleşme skoru düşük; doğrudan yeterlilik yerine POTANSİYEL vurgusu yap. "
    "Adayın öğrenme hızını, aktarılabilir (transferable) becerilerini, motivasyonunu ve "
    "gelişim eğilimini öne çıkar; eksik becerileri hızlı kapatabileceğine dair somut "
    "işaretler ver. Abartılı yeterlilik iddialarından kaçın."
)


def select_strategy(matching_gaps: dict[str, Any]) -> str:
    """Skor < LOW_SCORE_THRESHOLD ise potansiyel vurgusu, aksi halde standart strateji."""
    score = (matching_gaps or {}).get("score")
    if isinstance(score, (int, float)) and score < LOW_SCORE_THRESHOLD:
        return STRATEGY_POTENTIAL
    return STRATEGY_STANDARD
