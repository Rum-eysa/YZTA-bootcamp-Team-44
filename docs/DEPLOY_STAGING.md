# Staging Deploy Runbook (US-035)

Hedef: Backend **Railway**'de, frontend **Vercel**'de, veritabanı **Supabase**'de (zaten migrate'li).
Bu doküman sıfırdan staging kurulumunun tüm adımlarını içerir. Tahmini süre: ~30 dk.

## Mimari (staging)

```
Vercel (Next.js)  ──HTTPS──▶  Railway: api (FastAPI, Dockerfile)
                                 │── Railway: Redis (plugin)
                                 │── Railway: minio (minio/minio image, public domain)
                                 └── Supabase PostgreSQL (mevcut, SUPABASE_DB_URL)
```

- **DB:** Yeni bir staging DB açmaya gerek yok — ekibin Supabase projesi kullanılır.
  `railway.json` start komutu her deploy'da `alembic upgrade head` çalıştırır (migrate kriteri).
- **Redis:** Gemini kota sayacı + JWT blacklist için zorunlu → Railway Redis plugin.
- **MinIO:** CV PDF'leri için. Railway'de `minio/minio` image'ıyla ayrı servis olarak koşar;
  PDF linklerinin tarayıcıdan açılabilmesi için public domain verilir.

## 1) Backend — Railway

1. [railway.app](https://railway.app) → GitHub ile giriş → **New Project → Deploy from GitHub repo** → `Rum-eysa/YZTA-bootcamp-Team-44` seç.
   Kökteki `railway.json` otomatik algılanır (Dockerfile: `apps/api/Dockerfile`, start: migrate + uvicorn, healthcheck: `/health`).
2. Aynı projeye **+ New → Database → Redis** ekle.
3. Aynı projeye **+ New → Empty Service** → Source: Docker Image → `minio/minio` →
   Start Command: `minio server /data --console-address :9001` →
   Variables: `MINIO_ROOT_USER`, `MINIO_ROOT_PASSWORD` (güçlü değerler) →
   Settings → Networking → **Generate Domain** (public, port 9000).
4. **api servisinin Variables** sekmesine aşağıdaki değişkenleri gir (bkz. tablo).
5. api servisine **Generate Domain** ver → `https://<api-domain>` not al.
6. Deploy loglarında `alembic upgrade head` çıktısını ve healthcheck'in geçtiğini doğrula.

### api servisi environment değişkenleri

| Değişken | Değer | Not |
|---|---|---|
| `DATABASE_URL` | Supabase session-pooler URL'si (`.env`'deki `SUPABASE_DB_URL` değeri) | port 5432, transaction pooler değil |
| `REDIS_URL` | `${{Redis.REDIS_URL}}` | Railway reference |
| `JWT_SECRET` | yeni üret: `openssl rand -base64 32` | local ile aynı OLMASIN |
| `GEMINI_API_KEY` | ekip anahtarı | kota paylaşımlı (~18/gün), demo öncesi harcamayın |
| `GEMINI_MODEL` | `gemini-flash-latest` | |
| `STORAGE_ENDPOINT` | `http://<minio-servis-adı>.railway.internal:9000` | private network |
| `STORAGE_ACCESS_KEY` / `STORAGE_SECRET_KEY` | MinIO root user/password | |
| `STORAGE_BUCKET` | `cv-documents` | api açılışta bucket'ı oluşturur |
| `STORAGE_PUBLIC_URL` | `https://<minio-public-domain>` | PDF linkleri buradan servis edilir |
| `CORS_ORIGINS` | `https://<vercel-domain>` | frontend origin(ler)i |
| `ALLOWED_HOSTS` | `<api-domain>` | TrustedHost için API'nin KENDİ domain'i (yoksa 400 döner) |
| `ENVIRONMENT` | `staging` | |
| `DEBUG` | `false` | `/docs` kapanır - istenirse staging'de `true` bırakılabilir |
| `LOG_LEVEL` | `info` | |
| `SENTRY_DSN` | (opsiyonel) | boşsa devre dışı |

## 2) Frontend — Vercel

1. [vercel.com](https://vercel.com) → GitHub ile giriş → **Add New → Project** → repo'yu seç.
2. **Root Directory:** `apps/web` (monorepo!). Framework: Next.js (otomatik algılar).
3. Environment Variables: `NEXT_PUBLIC_API_URL = https://<api-domain>` (Railway'den).
4. Deploy → çıkan `https://<proje>.vercel.app` domain'ini not al.
5. Railway'e dön: api servisinin `CORS_ORIGINS` değerine bu Vercel domain'ini yaz → redeploy.

## 3) Seed verisi (staging'de)

Railway CLI ile (yerelden, `railway login` + `railway link` sonrası):

```bash
railway run --service api python scripts/seed_database.py
```

Alternatif: Railway dashboard → api servisi → Settings → **One-off Command**:
`python scripts/seed_database.py`

> Dikkat: seed, mevcut users/listings/matches/documents tablolarını TEMİZLEYİP yeniden doldurur.
> Supabase paylaşılan DB olduğu için ekibe haber vermeden çalıştırmayın.

## 4) Doğrulama (kabul kriterleri)

```bash
curl https://<api-domain>/health          # {"status":"healthy",...}
curl https://<api-domain>/health/ready    # DB+Redis bağlantısı dahil 200
```

- [ ] Vercel URL tarayıcıda açılıyor, login/register çalışıyor
- [ ] `POST /api/analyze` staging'de bir ilanı işliyor (1 Gemini isteği harcar)
- [ ] CV üret → dönen `cv_url` (MinIO public domain) tarayıcıda PDF açıyor

## Sorun giderme

- **Tüm istekler 400 "Invalid host header"** → `ALLOWED_HOSTS`'a API'nin Railway domain'i yazılmamış.
- **CORS hatası** → `CORS_ORIGINS`'te Vercel domain'i yok ya da sonda `/` var (olmamalı).
- **PDF linki açılmıyor** → `STORAGE_PUBLIC_URL` MinIO'nun public domain'i değil; MinIO
  servisinde Generate Domain yapılmamış olabilir.
- **asyncpg prepared statement hatası** → `DATABASE_URL` transaction pooler (6543) kullanıyor;
  session pooler (5432) olmalı.
