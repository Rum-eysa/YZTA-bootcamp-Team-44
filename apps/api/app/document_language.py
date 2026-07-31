"""İlan bazlı CV/önyazı üretim dili (tr|en)."""

from typing import Optional

DOCUMENT_LANGUAGES = frozenset({"tr", "en"})
DEFAULT_DOCUMENT_LANGUAGE = "tr"

_LANGUAGE_NAMES = {
    "tr": "Türkçe",
    "en": "English",
}

# LaTeX bölüm başlıkları ve sabit UI metinleri
CV_LABELS: dict[str, dict[str, str]] = {
    "tr": {
        "summary": "Özgeçmiş Özeti",
        "experience": "Deneyimler",
        "education": "Eğitimler",
        "projects": "Projeler",
        "certificates": "Sertifikalar",
        "exams": "Sınavlar",
        "certificates_and_exams": "Sertifikalar ve Sınavlar",
        "languages": "Yabancı Dil",
        "references": "Referanslar",
        "photo_placeholder": "Fotoğraf",
        "photo_area": "Alanı",
        "certificate_prefix": "Sertifika",
        "exam_prefix": "Sınav",
        "certificates_heading": "Sertifikalar",
        "exams_heading": "Sınavlar",
        "gender": "Cinsiyet",
        "nationality": "Uyruk",
        "birth_year": "Doğum Yılı",
        "military_status": "Askerlik Durumu",
        "driver_license": "Sürücü Belgesi",
        "unspecified": "belirtilmemiş",
    },
    "en": {
        "summary": "Professional Summary",
        "experience": "Experience",
        "education": "Education",
        "projects": "Projects",
        "certificates": "Certificates",
        "exams": "Exams",
        "certificates_and_exams": "Certificates and Exams",
        "languages": "Languages",
        "references": "References",
        "photo_placeholder": "Photo",
        "photo_area": "Area",
        "certificate_prefix": "Certificate",
        "exam_prefix": "Exam",
        "certificates_heading": "Certificates",
        "exams_heading": "Exams",
        "gender": "Gender",
        "nationality": "Nationality",
        "birth_year": "Year of Birth",
        "military_status": "Military Status",
        "driver_license": "Driver License",
        "unspecified": "unspecified",
    },
}


def normalize_document_language(value: Optional[str]) -> str:
    """İzinli dil koduna çeker; bilinmeyen → tr."""
    if not value or not str(value).strip():
        return DEFAULT_DOCUMENT_LANGUAGE
    code = str(value).strip().lower()
    if code in ("tr", "turkish", "türkçe", "turkce"):
        return "tr"
    if code in ("en", "english", "ingilizce"):
        return "en"
    return DEFAULT_DOCUMENT_LANGUAGE


def language_display_name(code: Optional[str]) -> str:
    normalized = normalize_document_language(code)
    return _LANGUAGE_NAMES[normalized]


def cv_labels_for(code: Optional[str]) -> dict[str, str]:
    return CV_LABELS[normalize_document_language(code)]


def language_instruction(code: Optional[str]) -> str:
    """Prompt'a eklenecek dil talimatı (yalnızca allowlist)."""
    normalized = normalize_document_language(code)
    if normalized == "en":
        return (
            "CRITICAL — document language is English: write ALL output text in English "
            "(summary, job titles, descriptions, rewrites). Do not leave Turkish "
            "sentences. Proper nouns (company names, product names, city names) may "
            "stay as-is. Ignore the listing's language if it conflicts — the document "
            "language wins."
        )
    return (
        "CRITICAL — belge dili Türkçe: tüm çıktıyı Türkçe yaz. İngilizce yalnızca "
        "özel isim veya teknik terim gerekiyorsa kullan. İlan dili İngilizce olsa "
        "bile belge dili Türkçe ise Türkçe yaz."
    )


# Profil enum / seviye değerlerini belge diline taşı (etiket değil, değer).
# Anahtarlar ASCII-fold edilmiş küçük harf olmalı (_fold_tr).
_VALUE_TR_TO_EN: dict[str, str] = {
    "erkek": "Male",
    "kadin": "Female",
    "diger": "Other",
    "belirtmek istemiyorum": "Prefer not to say",
    "muaf": "Exempt",
    "yapildi": "Completed",
    "tecilli": "Deferred",
    "yapilmadi": "Not completed",
    "baslangic": "Beginner",
    "temel": "Elementary",
    "orta": "Intermediate",
    "iyi": "Upper-Intermediate",
    "ileri": "Advanced",
    "anadil": "Native",
    "ana dil": "Native",
    "native": "Native",
    "junior": "Junior",
    "mid": "Mid-level",
    "senior": "Senior",
    "belirtilmemis": "unspecified",
    "turkiye": "Turkey",
    "t.c.": "Turkey",
    "tc": "Turkey",
    "turk": "Turkish",
    "ingilizce": "English",
    "almanca": "German",
    "fransizca": "French",
    "ispanyolca": "Spanish",
    "arapca": "Arabic",
    "rusca": "Russian",
    "lisans": "Bachelor's",
    "on lisans": "Associate degree",
    "yuksek lisans": "Master's",
    "doktora": "PhD",
}

_TR_FOLD = str.maketrans(
    {
        "ı": "i",
        "İ": "i",
        "I": "i",
        "ğ": "g",
        "Ğ": "g",
        "ü": "u",
        "Ü": "u",
        "ş": "s",
        "Ş": "s",
        "ö": "o",
        "Ö": "o",
        "ç": "c",
        "Ç": "c",
    }
)


def _fold_tr(text: str) -> str:
    """Türkçe karakterleri ASCII'ye çevirip küçük harfe indirger (lookup için)."""
    return text.translate(_TR_FOLD).lower().replace("i\u0307", "i")


def localize_profile_value(value: Optional[object], lang: Optional[str]) -> str:
    """Cinsiyet / askerlik / dil seviyesi gibi kısa profil değerlerini diline çevirir."""
    if value is None:
        return ""
    text = str(value).strip()
    if not text:
        return ""
    if normalize_document_language(lang) != "en":
        return text
    mapped = _VALUE_TR_TO_EN.get(_fold_tr(text))
    return mapped or text
