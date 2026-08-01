# Deploy — CareerTrack

Backend **Railway**, frontend **Vercel**, veritabanı **Supabase PostgreSQL**.
`main`’e her merge otomatik deploy tetikler.

## Canlı URL’ler

| Servis | URL |
| --- | --- |
| Frontend | https://yzta-bootcamp-team-44.vercel.app |
| Backend API | https://yzta-bootcamp-team-44-production.up.railway.app |
| API Docs | https://yzta-bootcamp-team-44-production.up.railway.app/docs (`DEBUG=true` iken) |

Demo ve paylaşım için her zaman bu kalıcı Vercel alias’ını kullanın (hash’li preview URL’ler SSO arkasında olabilir).

## Mimari

```
Vercel (Next.js, apps/web)
    │ HTTPS
    ▼
Railway: api (FastAPI — apps/api/Dockerfile)
    ├── Railway Redis          # JWT blacklist, rate limit, Gemini kota
    ├── Railway MinIO          # CV / avatar dosyaları
    └── Supabase PostgreSQL    # paylaşılan DB (session pooler, port 5432)
```

Her API deploy’unda `railway.json` start komutu `alembic upgrade head` çalıştırır, ardından uvicorn ayağa kalkar. Healthcheck: `/health`.

## Ortam değişkenleri (API)

| Değişken | Açıklama |
| --- | --- |
| `DATABASE_URL` | Supabase session-pooler URL (port **5432**; transaction pooler 6543 kullanmayın) |
| `REDIS_URL` | Railway Redis referansı |
| `JWT_SECRET` | Güçlü gizli anahtar (`openssl rand -base64 32`) |
| `GEMINI_API_KEY` / `GEMINI_MODEL` | AI anahtarı ve model |
| `STORAGE_ENDPOINT` | MinIO private URL (`http://<servis>.railway.internal:9000`) |
| `STORAGE_ACCESS_KEY` / `STORAGE_SECRET_KEY` | MinIO kimlik bilgileri |
| `STORAGE_BUCKET` | `cv-documents` |
| `STORAGE_PUBLIC_URL` | MinIO public domain |
| `CORS_ORIGINS` | Vercel origin (sonda `/` olmasın) |
| `ALLOWED_HOSTS` | API’nin kendi Railway domain’i |
| `ENVIRONMENT` | `staging` veya `production` |
| `DEBUG` | Prod’da `false` |

Frontend (Vercel): `NEXT_PUBLIC_API_URL=https://<api-domain>` · Root Directory: `apps/web`.

## İlk kurulum (özet)

1. Railway’de repo’yu bağla (`railway.json` + `apps/api/Dockerfile` algılanır).
2. Aynı projeye Redis ve MinIO (`minio/minio`, public domain port 9000) ekle.
3. API değişkenlerini yukarıdaki tabloya göre doldur; domain üret; healthcheck’i doğrula.
4. Vercel’de projeyi ekle (`apps/web`), `NEXT_PUBLIC_API_URL` ver, deploy et.
5. Railway `CORS_ORIGINS` içine Vercel domain’ini yazıp API’yi yeniden deploy et.

## Seed (dikkatli kullan)

Seed, paylaşılan Supabase tablolarını temizleyip yeniden doldurur. Ekibe haber vermeden çalıştırmayın.

```bash
railway link   # ilgili proje / servis
railway ssh "python scripts/seed_database.py"
```

> `railway run` yalnızca env enjekte eder; bağımlılıklar yerelde yoksa script çalışmaz. Container içinde çalıştırmak için `railway ssh` kullanın.

## Doğrulama

```bash
curl https://<api-domain>/health
curl https://<api-domain>/health/ready
```

- Frontend açılıyor; login / register çalışıyor
- Landing’de misafir ATS veya girişli ilan analizi çalışıyor
- İlan detayında eşleşme, CV ve önyazı üretimi tamamlanıyor

## Sorun giderme

| Belirti | Olası neden |
| --- | --- |
| Tüm istekler 400 Invalid host | `ALLOWED_HOSTS`’a API domain’i yazılmamış |
| CORS hatası | `CORS_ORIGINS` eksik veya sonda `/` var |
| asyncpg prepared statement | `DATABASE_URL` transaction pooler (6543); session pooler (5432) kullanın |
| Feature branch yansımaz | Deploy yalnızca `main` merge sonrası tetiklenir |
