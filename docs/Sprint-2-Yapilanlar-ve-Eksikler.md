# Sprint 2 — Yapılanlar ve Eksikler

**Tarih:** 19 Temmuz 2026  
**Amaç:** Sprint 2 planına göre nelerin tamamlandığını, hangi kabul kriterlerinin kısmen kaldığını ve Sprint 3’e taşınanları tek yerde listelemek.  
**Kaynaklar:** `Sprint Planı.md`, `Sprint 2 Kalan İşler ve Yeni User Story'ler.md`, `Sprint 2'de eklenmesini istediklerim.md` + güncel kod denetimi.

**Özet verdict:** Sprint 2 must-have’lerinin büyük çoğunluğu kodda kapanmış durumda (**~33 tam / 2 kısmi / ~88–90 SP**). Ana ürün akışı (ilan analizi → eşleşme → CV/önyazı → `/listings/:id`) çalışıyor. Kalan boşluklar çoğunlukla UX cilası (US-036 sticky), orkestratör sıra AC uyumu (US-041) ve Sprint 3’e planlanan ATS/CV genişliği ile UAT işleridir.

---

## 1. Tamamlanan story’ler

Aşağıdakilerde kabul kriterlerinin tamamı (veya ürün kararıyla eşdeğer alternatif) kodda karşılanıyor.

| Story | Başlık | SP | Kanıt (kısa) |
|-------|--------|----|--------------|
| US-002† | Supabase Borç Kapatma | 2 | `ARCHITECTURE.md` MinIO/Supabase kapsamı; `.env.example` yorumları |
| US-006† | Layout Borç Kapatma | 2 | `AppLayout` + `AppSidebar` (Profil / İlan Ekle / Başvurulan İlanlar), mobil menü |
| US-008† | Profil Borç Kapatma | 2 | Profilde `seniority`, `experience_years`; `PATCH /api/profiles/me` |
| US-009† | İlan Girişi Borç Kapatma | 1 | `/apply` ton tercihi + metin validation; redirect `/listings/:id` (US-039 ürün kararı) |
| US-010† | Seed Borç Kapatma | 1 | `matches` + `documents` seed; `make seed` özeti; README demo hesapları (US-038 ile birlikte) |
| US-013 | İş Deneyimi & Proje Şeması | 3 | Migration 004/005; CRUD `profiles` routes; model/schema/repo |
| US-014 | Analysis Agent: Tamamlama | 1 | `GET /api/listings/:id` analiz sonucunu DB’den döner |
| US-015 | CV Generation Agent: API Wiring | 2 | `POST /api/generate-cv`; Tectonic → MinIO → `documents` |
| US-016 | Matching Agent: API Wiring | 2 | Matching agent + kalıcı `matches` |
| US-017 | Memory Layer: Context Manager | 2 | `services/context.py`; CV/match/önyazı/orchestrator kullanıyor |
| US-018 | Logging + Sentry | 2 | `observability.py`, `init_sentry()`, agent telemetrisi + testler |
| US-019 | Frontend: İş Deneyimi CRUD | 4 | Profil sayfası + `ExperienceModal` + API client |
| US-020 | Frontend: Proje CRUD | 2 | Profil sayfası + `ProjectModal` + API client |
| US-021 | Matching: Skor Sistemi | 3 | Breakdown (required / nice / seniority / semantic); deneyim/proje etkisi |
| US-022 | Cover Letter Agent: API Wiring | 3 | `POST /api/generate-cover-letter`; tone; skor&lt;40 potansiyel stratejisi |
| US-023 | API: `/api/match` | 2 | Auth, schema, persistence; sahiplik US-040 ile kapatıldı |
| US-024 | Score Gauge (Results UI) | 5 | `/listings/:id` üzerinde `ScoreGauge` + renk bantları + breakdown |
| US-025 | API: generate-cv & cover-letter | 2 | Her iki endpoint production-ready |
| US-026 | Skill Comparison Table | 5 | Beceri tablosu, arama/filtre, durum/kategori; match API verisi |
| US-027 | CV Preview + Download | 3 | iframe önizleme, indir, loading/hata toast |
| US-028 | Cover Letter View | 3 | Metin, kopyala+toast, kelime/karakter sayacı, düşük skor ipucu |
| US-029 | Job Form → `/api/analyze` | 2 | `/apply` → analyze → `/listings/:id` |
| US-030 | Orchestrator | 5 | `POST /api/process`; ContextManager; adım retry |
| US-031 | API E2E Testler (Backend) | 1 | Route seviyesinde pipeline testleri |
| US-032 | Results Page API Integration | 4 | React Query; `sessionStorage` analiz workaround yok; refresh → API |
| US-033 | Agent Unit Tests (%80+) | 2 | `test_gemini_client.py`; CI `app/agents/*` `--fail-under=80` |
| US-034 | E2E Integration Tests | 5 | `test_e2e.py` (register → … → cover letter); mock dış servisler |
| US-035 | Staging Deploy | 3 | Railway + Vercel; `docs/DEPLOY_STAGING.md` |
| US-037 | Yeniden Analiz & Eşleştirme | 5 | `Yeniden Analiz Et` / `Eşleşmeyi Güncelle`; rematch; stale uyarı; `analyzed_at`; testler |
| US-038 | Zengin Seed | 2 | Deneyim, proje, eğitim, sertifika seed; README demo hesapları |
| US-039 | `/results` kaldırma | 3 | Tek sayfa `/listings/:id`; `app/results/` yok |
| US-040 | Match sahiplik kontrolü | 1 | `created_by` → 403/404; `test_match_route.py` |
| US-042 | CV route hata testleri | 1 | 422 (LaTeX) + 503 (servis) integration testleri |

**Erken tamamlanan (Sprint 3 kartı, kodda hazır):**

| Story | Başlık | Not |
|-------|--------|-----|
| US-045 | Landing Page Yenileme | `app/page.tsx` — fark bölümleri + CTA’lar mevcut |
| US-046 | Staging/Production Deploy | `docs/deploy.md` canlı URL’ler + go-live checklist |

---

## 2. Kısmen tamamlanan

### US-036 — İlan Düzenleme: Kaydet Butonu UX (2 SP)

| Kriter | Durum |
|--------|--------|
| Form sonunda ikinci “Değişiklikleri Kaydet” | ✅ (`ListingEditActions` sayfa altı) |
| Üstte kaydet alanı | ✅ (header kartında) |
| Sticky header / kaydırınca üstte sabit kalma | ⚠️ Sticky değil; yalnızca form başında |
| Kaydet primary / İptal outline | ✅ |
| Aynı `handleSave` | ✅ |

**Eksik:** Üst aksiyonların sticky davranışının netleşmesi / kontrastın “zıt renk” beklentisinin tasarım incelemesi.

### US-041 — Orchestrator sıra / retry / response (2 SP)

| Kriter | Durum |
|--------|--------|
| Exponential backoff, max 2 deneme | ✅ |
| Response: `listing_id`, `match`, `cv_url`, `cover_letter_text`, `errors[]` | ✅ |
| Agent sırası: Analysis → Matching → **CV → Cover Letter** | ❌ Kodda: Analysis → Matching → **Önyazı → CV** |

**Eksik:** AC’deki CV→önyazı sırası ile implementasyon ters; bilinçli ürün kararı değilse düzeltilmeli veya AC güncellenmeli.

### Diğer küçük boşluklar (story dışı / borç)

| Konu | Durum |
|------|--------|
| RLS yeni tablolarda (`work_experiences`, `projects`, eğitim vb.) | ⚠️ Core tablolarda RLS var; genişleme tablolarında yok (defense-in-depth; API service_role) |
| Önyazı UI düşük skor eşiği (`score < 70`) vs agent stratejisi (`score < 40`) | ⚠️ İkisi de çalışıyor; eşikler hizalı değil |
| Profil deneyim/proje fetch’i React Query değil `useState` | ⚠️ İşlevsel; US-032 kapsamı listing sonuçları için kapatıldı |

---

## 3. Yapılmayan / Sprint 3’e kalan

| Story | Başlık | SP | Durum |
|-------|--------|----|--------|
| US-043 | ATS-Uyumlu LaTeX CV Şablonu | 5 | ❌ Mevcut minimal `cv_template.tex.jinja`; ATS araştırma/şablon değişimi yok |
| US-044 | CV’de Tam Profil Verisi | 5 | ⚠️ Kısmen: deneyim, proje, eğitim var; sertifika, dil, referans, sosyal link, ilan `required_skills`/`nice_to_have` şablonda eksik/kısıtlı |
| US-047 | UAT ve Son Sistem Testleri | 3 | ❌ `docs/sprints/us-047-uat-report.md` iskelet; demo UAT tamamlanmamış (`docs/deploy.md` checklist açık maddeler) |
| US-048 | Sprint Retro / kapanış (varsa) | — | Sprint 3 kapanış işi |

> US-045 ve US-046 Sprint 3 etiketi taşısa da kod/deploy tarafında büyük ölçüde hazır; resmi kapanış ve UAT Sprint 3’te.

---

## 4. Wishlist çapraz kontrol

Kaynak: `Sprint 2'de eklenmesini istediklerim.md`

| # | İstek | Karşılık | Sonuç |
|---|--------|----------|--------|
| 1 | İlan kaydet butonu üst+alt, zıt renkler | US-036 | ⚠️ Kısmen — alt+üst var; sticky eksik |
| 2 | ATS uyumlu LaTeX / Overleaf şablonu | US-043 | ❌ Sprint 3 |
| 3 | İlan değişince eşleşme + zorunlu beceriler yeniden | US-037 | ✅ Yeniden analiz / eşleşmeyi güncelle + stale uyarı |
| 4 | Düşük eşleşmede motivasyon odaklı daha iyi önyazı | US-022 + UI ipucu | ⚠️ Agent’ta skor&lt;40 “potansiyel” stratejisi var; “ileriye dönük motivasyon” için ayrı iyileştirme Sprint 3’e bırakılabilir |
| 5 | Seed’e eğitim, proje vb. | US-038 | ✅ |
| 6 | CV’de deneyim, proje, konum, skills, eğitim, sertifika, dil, referans, sosyal | US-044 | ⚠️ Kısmen (deneyim/proje/eğitim); geri kalan Sprint 3 |
| 7 | Ana sayfa fark vurgusu | US-045 | ✅ Erken tamamlandı |

---

## 5. 13 Temmuz “Kalan İşler” dosyasına göre delta

O tarihte In Progress / Todo görünenler ve **şimdi** durum:

| O zaman | Story | Şimdi |
|---------|-------|--------|
| In Progress | US-028 (sayacı/ipucu) | ✅ Tamam |
| In Progress | US-032 (React Query / sessionStorage) | ✅ Tamam |
| In Progress | US-033 (gemini test + %80 gate) | ✅ Tamam |
| Todo | US-024, US-026 | ✅ `/listings/:id` üzerinde |
| Todo | US-035 staging | ✅ (+ US-046 deploy) |
| Yeni must-have | US-037, US-039 | ✅ |
| Yeni | US-036, US-040, US-041, US-042, US-038 | ✅ / ⚠️ (036, 041 kısmi) |

---

## 6. Kaynaklar

- [Sprint Planı.md](../Sprint%20Planı.md) — US-002†…US-035 kabul kriterleri  
- [Sprint 2 Kalan İşler ve Yeni User Story'ler.md](../Sprint%202%20Kalan%20İşler%20ve%20Yeni%20User%20Story'ler.md) — board senkronu + US-036…048  
- [Sprint 2'de eklenmesini istediklerim.md](../Sprint%202'de%20eklenmesini%20istediklerim.md) — wishlist  
- README Sprint 2 özeti: [../README.md](../README.md#sprint-2)  
- Görseller: [docs/sprint-2/](./sprint-2/)
