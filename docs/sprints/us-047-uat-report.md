# US-047 — Staging UAT / Smoke Test Raporu

**Tarih:** 2026-07-16
**Ortam:** staging (Railway `yzta-bootcamp-team-44-production.up.railway.app` + Vercel `yzta-bootcamp-team-44.vercel.app`)
**Yöntem:** API'ye doğrudan `curl` ile uçtan uca senaryo + edge case'ler; frontend sayfaları smoke-check (sayfa yükleniyor mu).

## Ana Senaryo: register → profil → ilan ekle → listings detay → match → CV → önyazı

| Adım | Endpoint | Sonuç |
|---|---|---|
| Kayıt | `POST /api/auth/register` | ✅ 201 |
| Giriş | `POST /api/auth/login` | ✅ 200 |
| Profil güncelleme | `PATCH /api/profiles/me` | ✅ 200 |
| İlan ekle (analiz) | `POST /api/analyze` | ✅ 200 |
| İlan listesi | `GET /api/listings` | ✅ 200 |
| İlan detayı | `GET /api/listings/{id}` | ✅ 200 |
| Eşleştirme | `POST /api/match` | ✅ 200 (skor 80.0) |
| CV üretimi | `POST /api/generate-cv` | ✅ 200, PDF gerçek ve açılıyor (10KB, geçerli PDF) |
| Önyazı üretimi | `POST /api/generate-cover-letter` | ✅ 200, ~400 kelime tutarlı metin |

**Sonuç: Ana senaryo tamamen geçti.**

## Edge Case'ler

| Senaryo | Sonuç |
|---|---|
| **Düşük skor önyazı** — kullanıcı becerileriyle tamamen alakasız ilan (Rust/gömülü sistemler) | ✅ Skor 0.0 doğru hesaplandı, önyazı beceri açığını dürüstçe kabul edip motivasyona vurgu yapan makul bir metin üretti (çökme yok) |
| **İlan düzenleme + re-analyze** — `PATCH` ile `raw_text` değiştirilip `POST /reanalyze` çağrıldı | ⚠️ Kısmen geçti — `required_skills`/`seniority` doğru güncellendi, eski skor doğru şekilde sıfırlandı (`score: null`), ama **2 bug bulundu** (aşağıda) |
| **Boş profil** — hiç profil bilgisi girilmemiş yeni kullanıcı ile tam akış | ✅ Çökme yok; CV'de "Deneyim özeti eklenmedi." gibi makul fallback metinler, önyazı ilanın gereksinimlerine odaklanan tutarlı bir metin üretti |

## Bulunan Bug'lar (GitHub Issue)

| # | Başlık | Önem |
|---|---|---|
| [#98](https://github.com/Rum-eysa/YZTA-bootcamp-Team-44/issues/98) | `/reanalyze` ilan `title`/`company` alanlarını güncellemiyor | Orta — kullanıcıya yanlış başlık gösteriliyor |
| [#99](https://github.com/Rum-eysa/YZTA-bootcamp-Team-44/issues/99) | Analiz Ajanı `required_skills`'e deneyim süresi ifadesi ("5+ yıl deneyim") karıştırıyor | Orta — skor hesaplamasını haksız düşürüyor |
| [#100](https://github.com/Rum-eysa/YZTA-bootcamp-Team-44/issues/100) | Gemini günlük kota dolunca kullanıcıya anlaşılır mesaj gösterilmiyor | Düşük/Orta — demo günü gerçek risk |

## Operasyonel Not (kritik, demo öncesi ekiple paylaşılmalı)

UAT başladığında **günlük Gemini kotası zaten tükenmişti** (ekip içi test kullanımından, benim testimden önce). `gemini:quota:day` Redis sayacı 19/18'deydi. ~23 dakika TTL bitimini bekleyip devam edildi. **Demo günü bu riski azaltmak için**: demo saatinden hemen önce ekip Gemini gerektiren testleri durdurmalı, ya da ikinci bir API key değerlendirilmeli.

## Frontend Smoke Check

`/`, `/login`, `/register`, `/listings` sayfaları Vercel production alias'ında 200 dönüyor. Tam UI etkileşimi (form doldurma, tıklama akışı) bu turda test edilmedi — API seviyesinde uçtan uca doğrulandı.

## Sonuç

Ana akış ve 3 edge case staging'de manuel olarak test edildi, sistem beklenen şekilde çalışıyor. 3 bug GitHub issue olarak açıldı, biri (kota UX'i) demo riski taşıyor. Sprint Review'da paylaşılacak.
