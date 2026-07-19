# Go-Live Checklist (US-046)

Kurulum adımları için bkz. [`DEPLOY_STAGING.md`](./DEPLOY_STAGING.md) (US-035, değiştirilmedi).
Bu doküman US-046 kapsamında yapılan **fiili deploy**'un durumunu ve demo öncesi
son kontrol listesini içerir.

## Canlı URL'ler

| Servis | URL | Durum |
|---|---|---|
| Backend (Railway) | `https://yzta-bootcamp-team-44-production.up.railway.app` | ✅ `/health` ve `/health/ready` → 200 |
| Frontend (Vercel) | `https://yzta-bootcamp-team-44.vercel.app` | ✅ 200 (kalıcı production alias) |
| API Docs | `https://yzta-bootcamp-team-44-production.up.railway.app/docs` | `DEBUG=true` iken açık |

> Not: Vercel'in deployment-hash'li URL'i (`...-<hash>-zmd1.vercel.app`) Vercel SSO
> koruması arkasındadır ve demoda kullanılmamalı — her zaman yukarıdaki kalıcı
> `yzta-bootcamp-team-44.vercel.app` alias'ı paylaşılmalı.

## Go-Live Kontrol Listesi

- [x] Backend Railway'de ayakta, `/health` → `{"status":"healthy",...}` (200)
- [x] Backend Railway'de ayakta, `/health/ready` → DB+Redis dahil (200)
- [x] Frontend Vercel production alias'ında ayakta (200)
- [x] Staging DB migration güncel: her deploy başlangıcında `alembic upgrade head`
      çalışıyor (`railway.json` start command), deploy log'unda doğrulandı
- [x] Ortam değişkenleri senkron: `DATABASE_URL` (Supabase session pooler),
      `GEMINI_API_KEY`, `GEMINI_MODEL`, `JWT_SECRET`, `REDIS_URL`,
      `STORAGE_*` (MinIO), `CORS_ORIGINS` (Vercel domain'iyle eşleşiyor)
- [x] `make seed` staging'de çalıştırıldı (bkz. "Seed nasıl çalıştırılır")
      — 5 kullanıcı, 6 ilan, 6 iş deneyimi, 9 proje, 6 eğitim, 4 sertifika,
      1 eşleştirme, 1 doküman
- [ ] Demo öncesi Gemini kotası kontrol edildi (paylaşımlı anahtar, ~18 istek/gün
      free tier — bkz. [[project_yzta_bootcamp]] risk notu)
- [ ] Demo senaryosu uçtan uca prova edildi (login → ilan yapıştır → analiz →
      eşleştirme → CV/önyazı üret)

## Seed nasıl çalıştırılır (staging, Railway SSH ile)

```bash
railway link -p e0e35eb0-c53e-4139-897f-88f179ebd9ea \
  -e 3a5f8d15-d69c-4fb3-ad1c-917498fe521a \
  -s 58041834-2ebc-47da-aabc-f21777251900
railway ssh "python scripts/seed_database.py"
```

> `railway run` **yerel makinede** çalışır, sadece env değişkenlerini Railway'den
> enjekte eder — Python bağımlılıkları yerelde kurulu değilse (bu repoda öyle)
> çalışmaz. Container **içinde** çalıştırmak için `railway ssh` kullanılmalı.
> SSH ilk kullanımda `railway ssh keys add` ile bir anahtar kaydı gerektirir.

**Dikkat:** Supabase paylaşılan DB'dir, seed script'i `users/job_listings/matches/
documents/work_experiences/education_records/projects/certificates` tablolarını
TEMİZLEYİP yeniden doldurur. Ekiple haber vermeden çalıştırmayın.

## Deploy akışı

Railway, `main` branch'ine push'ta otomatik build+deploy tetikler (kökteki
`railway.json`, Dockerfile: `apps/api/Dockerfile`). Feature branch'lerdeki
değişiklikler staging'e yansımaz — önce main'e merge edilmeli.

Vercel, aynı repoyu (`apps/web` root directory) izler; `main`'e her push'ta
production deploy tetiklenir.

## Sorun giderme

Bkz. [`DEPLOY_STAGING.md`](./DEPLOY_STAGING.md#sorun-giderme).
