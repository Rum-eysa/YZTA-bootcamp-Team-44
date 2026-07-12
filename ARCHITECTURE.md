# Mimari Kararlar — CareerTrack (YZTA Bootcamp Team 44)

> Bu doküman, koddan okunamayan **bilinçli mimari kararları** kayda geçirir.
> Detaylı sistem tasarımı (agent diyagramları, veri akışı) US-041 kapsamında genişletilecektir.

## Supabase Kapsamı: Yalnızca PostgreSQL

Supabase bu projede **yalnızca yönetilen (managed) PostgreSQL veritabanı** olarak kullanılır.
Bu bir eksik değil, Sprint 1'de verilmiş bilinçli bir mimari karardır.

| Supabase özelliği | Durum | Karar gerekçesi |
|---|---|---|
| **PostgreSQL** | ✅ Kullanılıyor | Ekip tek paylaşılan veritabanına `SUPABASE_DB_URL` ile bağlanır; yönetim/yedekleme Supabase'de |
| **Supabase Auth** | ❌ Kullanılmıyor | Kimlik doğrulama FastAPI tarafında kendi JWT sistemimizle (bcrypt + Redis token blacklist) yapılır. Gerekçe: agent endpoint'lerinin tamamı backend'de; Supabase Auth eklemek ikinci bir kimlik katmanı ve frontend SDK bağımlılığı getirirdi |
| **Supabase Storage** | ❌ Kullanılmıyor | CV PDF'leri MinIO'da saklanır (aşağıya bakın) |
| **Supabase SDK** (`supabase-py`, JS client) | ❌ Kullanılmıyor | Veritabanına SQLAlchemy 2.0 + asyncpg ile doğrudan bağlanılır; ORM/migration (Alembic) akışı SDK'sız çalışır |

**Ortam değişkeni kapsamı:**
- **Kullanılan:** `SUPABASE_DB_URL` (docker-compose bunu `DATABASE_URL` olarak API'ye geçirir; boşsa yerel `postgres` container'ına düşülür)
- **Kullanılmayan (ileride gerekebilir diye .env'de tutulur):** `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY` — kodda hiçbir yerde referans edilmez
- Backend `service_role` bağlantısıyla RLS'i bypass eder; RLS politikaları (migration 003) yalnızca anon key sızıntısına karşı savunma katmanıdır

## Dosya Depolama: CV PDF Akışı (MinIO)

CV PDF'leri **Supabase Storage'a değil, MinIO'ya** (S3-uyumlu, docker-compose içinde) yazılır.

**Akış:**

```
CVGenerationAgent.generate()
    │  1. Jinja2 → LaTeX kaynak (cv_template.tex.jinja, latex_escape ile injection koruması)
    │  2. Tectonic ile derleme (container içinde, 60s timeout + 1 retry)
    ▼
StorageService.upload_cv(user_id, pdf_bytes)
    │  3. MinIO'ya PUT: bucket=cv-documents, key=cv/{user_id}/{uuid}.pdf
    ▼
documents tablosu
    │  4. doc_type="cv", cv_url=STORAGE_PUBLIC_URL/cv-documents/cv/{user_id}/{uuid}.pdf
    ▼
Frontend "PDF'i İndir" butonu cv_url'i doğrudan açar
```

**Neden MinIO, neden Supabase Storage değil:**
- PDF üretimi tamamen backend'de olur (Tectonic API container'ına gömülü); dosyanın üretildiği yerde S3-uyumlu bir hedefe yazmak tek network sıçraması demektir
- MinIO docker-compose'da ekiple birlikte ayağa kalkar → yerel geliştirme internet/Supabase hesabı gerektirmez
- S3-uyumlu arayüz sayesinde production'da MinIO yerine AWS S3/Cloudflare R2'ye `STORAGE_ENDPOINT` değişikliğiyle geçilebilir; Supabase Storage'a kilitlenmek bu esnekliği kaybettirirdi
- Not: MinIO **yereldir** — her geliştiricinin PDF'leri kendi makinesinde durur, ekip arasında paylaşılmaz (veritabanındaki `cv_url` başka makinede çözünmeyebilir; demo tek makineden yapılır)

## Kimlik Doğrulama: Kendi JWT Sistemimiz

- `POST /api/auth/register|login|refresh|logout` — FastAPI + `python-jose` JWT + bcrypt
- Logout, token'ın `jti`'sini Redis blacklist'ine yazar
- Korumalı endpoint'ler `Authorization: Bearer <token>` bekler (`get_current_user_id` dependency)
- Supabase Auth devreye alınmadığı için RLS'teki `auth.uid()` politikaları bizim JWT'mizle eşleşmez — bu bilinçlidir (yukarıya bakın)
