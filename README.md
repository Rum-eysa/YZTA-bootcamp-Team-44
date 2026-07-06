# YZTA Bootcamp - AI Destekli Staj Başvuru Platformu

<div align="center">

![YZTA Bootcamp](https://img.shields.io/badge/YZTA-Bootcamp-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green)
![Next.js](https://img.shields.io/badge/Next.js-14.2-black)
![Python](https://img.shields.io/badge/Python-3.11-blue)
![License](https://img.shields.io/badge/License-MIT-yellow)

**Yapay zeka destekli kişiselleştirilmiş CV ile önyazı oluşturma ve başvuru takip platformu**

[Ürün Özellikleri](#ürün-özellikleri) • [Sprint Planı](#sprint-planı) • [Mimari](#mimari) • [Hızlı Başlangıç](#hızlı-başlangıç) • [API Dokümantasyonu](#api-dokümantasyonu) • [Katkıda Bulunma](#katkıda-bulunma)

</div>

---

Projede, birden fazla iş ilanına başvuran adaylar için yapay zeka destekli bir kariyer platformudur. Her ilanın farklı beklentilerini analiz ederek kullanıcının CV'sini o ilana göre günceller, önyazısını oluşturur ve tüm başvurularını tek bir yerden takip etmesini sağlar.

## Takım İsmi

Takım 44

## Takım Rolleri

| Rol | Kişi | GitHub |
|-----|------|--------|
| Product Owner | Rumeysa AĞIL| [@Rum-eysa](https://github.com/Rum-eysa) |
| Scrum Master | Serkan YILDIZ | [@Serkan0YLDZ](https://github.com/Serkan0YLDZ) |
| Developer | Zeynep Maide DEMİR| [@zeynepmaidedemir](https://github.com/zeynepmaidedemir) |
| Developer | Filiz Buzkıran | [@lizlavigne](https://github.com/lizlavigne) |

## Ürün İsmi

CareerTrack - AI destekli kişiselleştirilmiş CV ile önyazı oluşturma ve başvuru takip platformu

## Ürün Açıklaması

Kullanıcılar farklı şirketlere ve pozisyonlara aynı anda başvurabilir; ancak her iş ilanı farklı beceri ve deneyim beklentisi içerir. Platform, ilan metnini yapay zeka ile inceleyerek hangi özelliklerin arandığını çıkarır, kullanıcının o ilanda öne çıkması için CV'sini ilana özel şekilde günceller ve önyazısını oluşturur. Başvurulan tüm ilanlar da platform üzerinden takip edilebilir.

## Problem Tanımı

Birçok iş ilanına başvuran adaylar, her pozisyonun farklı gereksinimleri nedeniyle CV ve önyazılarını tek tek uyarlamak zorunda kalır. Bu süreç zaman alıcıdır ve başvuruların takibi dağınık hale gelebilir. Platform, ilanlardaki beklentileri otomatik analiz ederek adayın her başvuruya uygun dokümanları hazırlamasına ve tüm süreci merkezi olarak yönetmesine yardımcı olur.

## İş Değeri

- Her iş ilanı için CV ve önyazıyı kişiselleştirir.
- İlanda aranan beceri ve deneyimleri net şekilde ortaya çıkarır.
- Adayın ilana uygunluğunu puanlayarak hangi başvurulara öncelik verileceğini gösterir.
- Tüm başvuruları tek platformda takip ederek süreci düzenli hale getirir.

## Ürün Özellikleri

- **AI Destekli İlan Analizi** - Google Gemini ile iş ilanındaki beceri ve deneyim beklentilerini çıkarma.
- **Kişiselleştirilmiş CV Üretimi** - Her ilana özel, öne çıkmayı hedefleyen CV güncellemesi.
- **Otomatik Önyazı** - İlan ve profil bilgisine göre önyazı oluşturma.
- **Başvuru Takibi** - Başvurulan tüm iş ilanlarını aşama ve durum bazında izleme.
- **Güvenli Kimlik Doğrulama** - JWT tabanlı kimlik doğrulama ve bcrypt şifreleme.
- **Yüksek Performans** - Redis önbellekleme katmanı ile asenkron işleme.
- **İzlenebilirlik** - Yapılandırılmış loglama ve istek takibi.
- **Kurumsal Güvenlik** - CORS, hız sınırlama, güvenlik başlıkları ve giriş doğrulama.
- **Kapsamlı Testler** - Yüksek kapsamlı birim ve entegrasyon testleri.
- **Sürekli Entegrasyon / Dağıtım** - GitHub Actions ile otomatik test ve dağıtım.
- **Veritabanı Göçleri** - Alembic ile versiyon kontrollü şema değişiklikleri.
- **Modern Arayüz** - TailwindCSS ve Next.js ile duyarlı kullanıcı arayüzü.

## Hedef Kitle

- Staj ve iş arayan öğrenciler
- Birden fazla pozisyona eş zamanlı başvuran adaylar
- Bootcamp ve kariyer geliştirme programı katılımcıları
- CV ve önyazısını her ilana göre uyarlamak isteyen kullanıcılar

## Ürün Backlog'u

Proje backlog bilgileri GitHub Projects üzerinden yönetilmektedir:

- [GitHub Projects Backlog](https://github.com/users/Rum-eysa/projects/6/views/1?groupedBy%5BcolumnId%5D=364119553)
- Sprint planları ve görev takibi burada güncellenmektedir
- Sprint 1 detayları için [Sprint 1](#sprint-1) bölümüne bakınız

## Sprint Planı

### Sprint 1

<details id="sprint-1">
<summary><strong>Sprint 1 detayları için tıklayın</strong></summary>

<br>

- **Product Backlog:** Backlog ve sprint görevleri [GitHub Projects](https://github.com/users/Rum-eysa/projects/6/views/1?groupedBy%5BcolumnId%5D=364119553) üzerinden yönetilmektedir. User story'ler `[US-00X]` formatında tanımlanmış; Status sütununda Todo, In Progress ve Done durumları takip edilmektedir.

  ![GitHub Project Board](docs/sprint-1/github-project-board.png)

- **Sprint Puanlaması:** Sprint 1 planı (19 Haziran – 5 Temmuz) toplam **62 story point** (12 user story). Story point'ler görev karmaşıklığına göre planlanmıştır (3–8 SP arası). Kod denetimi sonucu: **8 story tamamlandı**, **4 story kısmen tamamlandı** — kazanılan **~54 / 62 SP (%87)**. 

  | Story | Başlık | SP | Öncelik | Durum | Kazanılan | Eksik (Sprint 2'ye taşınan) | Sorumlu |
  | ----- | ------ | -- | ------- | ----- | --------- | --------------------------- | ------- |
  | US-001 | Proje Altyapısı Kurulumu | 8 | must-have | ✅ Tamamlandı | 8 | — | [@Rum-eysa](https://github.com/Rum-eysa) |
  | US-002 | Supabase Kurulumu | 5 | must-have | ⚠️ Kısmen | 3 | Supabase Auth/Storage yok; yalnızca DB bağlantısı + MinIO | [@zeynepmaidedemir](https://github.com/zeynepmaidedemir) |
  | US-003 | Veritabanı Şeması | 5 | must-have | ✅ Tamamlandı | 5 | `agent_tasks` migration drift (minor) | [@zeynepmaidedemir](https://github.com/zeynepmaidedemir) |
  | US-004 | SPIKE: LaTeX → PDF (Tectonic + Docker) | 8 | must-have | ✅ Tamamlandı | 8 | — | [@Serkan0YLDZ](https://github.com/Serkan0YLDZ) |
  | US-005 | Authentication Sistemi | 5 | must-have | ✅ Tamamlandı | 5 | `/api/analyze` JWT korumasız (minor) | [@zeynepmaidedemir](https://github.com/zeynepmaidedemir) |
  | US-006 | Frontend: Ana Layout + Header + Sidebar | 5 | must-have | ⚠️ Kısmen | 3 | Sidebar, mobil hamburger, dark mode | [@Serkan0YLDZ](https://github.com/Serkan0YLDZ) |
  | US-007 | Frontend: Login & Register Sayfaları | 5 | must-have | ✅ Tamamlandı | 5 | Server logout / token refresh UI (minor) | [@lizlavigne](https://github.com/lizlavigne) |
  | US-008 | Frontend: Kullanıcı Profil Formu | 5 | high | ⚠️ Kısmen | 3 | `seniority`, `experience_years`, `tone_preference`; deneyim/eğitim CRUD | [@lizlavigne](https://github.com/lizlavigne) |
  | US-009 | Frontend: İlan Girişi (metin / URL) | 3 | must-have | ⚠️ Kısmen | 2 | URL input gizli; ilan metadata API'ye gitmiyor | [@lizlavigne](https://github.com/lizlavigne) |
  | US-010 | Seed Verisi | 3 | high | ⚠️ Kısmen | 2 | `matches` / `documents` seed yok | [@zeynepmaidedemir](https://github.com/zeynepmaidedemir) |
  | US-011 | Temel Agent Sınıfı + Logging Framework | 5 | high | ✅ Tamamlandı | 5 | — (+ 4 domain agent bonus) | [@Rum-eysa](https://github.com/Rum-eysa) |
  | US-012 | Gemini API İstemci Wrapper'ı | 5 | must-have | ✅ Tamamlandı | 5 | — | [@zeynepmaidedemir](https://github.com/zeynepmaidedemir) |
  | | **Toplam** | **62** | | **8 tam · 4 kısmen** | **~54** | **~8 SP borç → Sprint 2** | |

  **Özet:** Planlanan 62 SP'nin ~54'ü kazanıldı. Kısmi story'lerde toplam ~8 SP'lik iş Sprint 2 borç listesine taşındı. Sprint 1 kapsamı dışında erken tamamlanan bonus işler: 4 AI agent modülü, `POST /api/analyze`, MinIO depolama (~62 pytest).

- **Daily Scrum:** Ekip 2 günde bir Slack Huddle üzerinden senkron toplantı yapmıştır. 

  *AI / Backend ilerleme paylaşımı — Zeynep'in agent sunumu:*

  ![Daily Scrum — Agent sunumu](docs/sprint-1/daily-scrum-agent-sunumu.png)

  *Frontend ilerleme paylaşımı — Serkan'ın UI prototip sunumu:*

  ![Daily Scrum — Frontend sunumu](docs/sprint-1/daily-scrum-frontend-sunumu.png)

- **Ürün Geliştirme Durumu:** Backend ve AI tarafında ilan analizi, aday uygunluk puanlama, kişiselleştirilmiş CV ve önyazı üretimi çalışır durumdadır (`POST /api/analyze`, Gemini client, agent framework, MinIO PDF depolama). Frontend tarafında CareerTrack arayüzünün profil ve ilan ekleme ekranları hazırlanmıştır; Next.js'te temel sayfalar mevcuttur (`login`, `register`, `profile`, `apply`).

  *Profil sayfası — kullanıcı bilgileri, özet ve beceriler:*

  ![Ürün durumu — Profil](docs/sprint-1/urun-durumu-profil.png)

  *İlan ekleme sayfası — şirket, pozisyon ve ilan detayları:*

  ![Ürün durumu — İlan Ekle](docs/sprint-1/urun-durumu-ilan-ekle.png)

- **Sprint Review:** Sprint 1 hedeflerinin büyük çoğunluğu tamamlandı (**~54 / 62 SP, %87**). Çıkan ürün testlerde kritik bir sorun göstermemiştir. 

  **Tamamlananlar:**
  - Monorepo altyapısı: FastAPI + Next.js + Docker Compose (PostgreSQL, Redis, MinIO)
  - Supabase/PostgreSQL şeması: `users`, `job_listings`, `matches`, `documents`
  - JWT authentication, Redis token blacklist, seed verisi (`make seed`)
  - AI agent katmanı: ilan analizi, eşleştirme, CV üretimi (Tectonic PDF), önyazı üretimi
  - `POST /api/analyze`, `PATCH /api/profiles/me`, Gemini client (rate limit, token tracking)
  - CareerTrack frontend: layout, login/register, profil ve ilan ekleme sayfaları; ilan analizi API entegrasyonu

  **Alınan kararlar:**
  - US-004: Standalone compiler kaldırıldı; Tectonic API Docker image içine gömüldü
  - `applications` CRUD yerine agent odaklı veri modeli benimsendi
  - İlan analizi sonuçları şimdilik frontend'de sessionStorage ile tutuluyor; kalıcı başvuru takibi Sprint 2'ye planlandı
  - CV/önyazı üretimi backend'de hazır; kullanıcı arayüzüne uçtan uca entegrasyon Sprint 2 kapsamına alındı

- **Sprint Retrospective:** 

  - **İyi giden:** Backend ve agent altyapısı erken tamamlandı.
  - **İyileştirme:** GitHub Projects board'u sprint sonu koxwd durumuyla senkron tutuldu.
  - **İyileştirme:** Kısmi story'lerde eksik AC'ler Sprint 2 borç listesine taşındı (~8 SP).
  - **Sprint 2 planlandı:** Sprint 1 retrospective sonrası Sprint 2 backlog'u revize edildi.

</details>

### Sprint 2

<details id="sprint-2">
<summary><strong>Sprint 2 ilerleme durumu için tıklayın</strong></summary>

<br>

**Backend — tamamlanan (PR #50 + sonrası):**
- `POST /api/match` — eşleştirme skoru (deterministik formül + Gemini semantik bonus, cache'li; Gemini erişilemezse deterministik skora düşer)
- `POST /api/generate-cover-letter` — şirkete özel önyazı (ilanın `company_name`'i prompt'a işlenir)
- `POST /api/generate-cv` — LaTeX/Tectonic ile PDF CV, MinIO'ya yüklenir
- `POST /api/analyze` — URL'den ilan çekme desteği eklendi
- Supabase RLS + sahiplik politikaları (migration 003)
- Ajan birim test kapsamı %89 (81 test, CI yeşil)
- Seed: matches/documents demo kayıtları eklendi

**Frontend — tamamlanan:**
- CareerTrack arayüzü: landing, login/register, profil, ilan girişi (metin + URL)
- Sonuç sayfası: analiz çıktısı + **uygunluk skoru göstergesi** + eşleşen/eksik beceri karşılaştırması + **önyazı üret/kopyala** + **CV üret/indir** bölümleri (`/analyze/[id]`)

**Devam eden / Sprint 3'e kalan:**
- İş deneyimi & proje şeması + CRUD (US-013/019/020)
- Orkestratör + hafıza katmanı (US-030, US-017)
- E2E entegrasyon testleri, Sentry, staging deploy

</details>

### Sprint 3


## Mimari

```
.
├── apps/
│   ├── api/                         # FastAPI Backend Service
│   │   ├── app/
│   │   │   ├── main.py              # Application entry point
│   │   │   ├── config.py            # Configuration management
│   │   │   ├── database.py          # Database connection
│   │   │   ├── models/              # SQLAlchemy ORM (User, JobListing, Match, Document)
│   │   │   ├── routes/              # API endpoints
│   │   │   │   ├── auth.py          # Authentication (/api/auth)
│   │   │   │   ├── users.py         # User management (/api/users)
│   │   │   │   ├── profiles.py      # Profile update (/api/profiles)
│   │   │   │   ├── analysis.py      # İlan analizi (/api/analyze)
│   │   │   │   ├── agents.py        # Agent task API (/api/agents)
│   │   │   │   └── health.py        # Health checks (/health)
│   │   │   ├── services/            # Business logic layer
│   │   │   │   ├── auth.py          # JWT, token blacklist
│   │   │   │   ├── user.py          # User service
│   │   │   │   ├── agent.py         # Agent task orchestration
│   │   │   │   ├── gemini_client.py # Google Gemini wrapper
│   │   │   │   ├── storage.py       # MinIO PDF depolama
│   │   │   │   └── listing_fetch.py # URL'den ilan metni çekme
│   │   │   ├── agents/              # AI agent modülleri
│   │   │   │   ├── listing_analysis.py
│   │   │   │   ├── matching.py
│   │   │   │   ├── cv_generation.py
│   │   │   │   └── cover_letter.py
│   │   │   ├── repositories/        # Veritabanı erişim katmanı
│   │   │   └── schemas/             # Pydantic request/response modelleri
│   │   ├── scripts/
│   │   │   └── seed_database.py     # Demo verisi (US-010)
│   │   ├── tests/                   # Test suite
│   │   ├── alembic/                 # Database migrations
│   │   └── Dockerfile
│   │
│   └── web/                         # Next.js Frontend Service
│       ├── app/                     # App Router
│       │   ├── page.tsx             # Landing page
│       │   ├── login/               # Giriş
│       │   ├── register/            # Kayıt
│       │   ├── profile/             # Profil formu
│       │   ├── apply/               # İlan girişi
│       │   └── analyze/[id]/      # Analiz sonuçları
│       ├── components/              # UI ve layout bileşenleri
│       ├── lib/                     # API client, validations
│       └── Dockerfile
│
├── docs/sprint-1/                   # Sprint dokümantasyon görselleri
├── .github/workflows/ci.yml         # CI/CD pipeline
├── docker-compose.yml               # Development (postgres, redis, minio, api, web)
├── docker-compose.prod.yml          # Production environment
├── Makefile                         # Command shortcuts
└── ...
```

### Teknoloji Stack

| Katman | Teknoloji | Amaç |
| --- | --- | --- |
| **Frontend** | Next.js 14, React 18, TypeScript, TailwindCSS | Duyarlı kullanıcı arayüzü |
| **Backend** | FastAPI, SQLAlchemy 2.0, Pydantic V2 | Yüksek performanslı async API |
| **Veritabanı** | PostgreSQL 15 / Supabase | Ana veri depolama |
| **Önbellek** | Redis 7 | Token blacklist ve önbellekleme |
| **Depolama** | MinIO (S3 uyumlu) | CV PDF dosya depolama |
| **AI/ML** | Google Gemini | İlan analizi, eşleştirme, CV ve önyazı üretimi |
| **PDF** | Tectonic (API image içinde) | LaTeX → PDF derleme |
| **Altyapı** | Docker, Docker Compose | Konteyner orkestrasyonu |
| **Test** | Pytest, pytest-asyncio, Coverage | Birim ve entegrasyon testleri |
| **CI/CD** | GitHub Actions | Otomatik test ve build |
| **Kod Kalitesi** | Black, isort, flake8, mypy, pre-commit | Linting ve formatlama |

## Hızlı Başlangıç

### Gereksinimler

- Docker & Docker Compose 20.10+
- Git
- Node.js 18+ (local development için)

### Kurulum

```bash
# Repository'yi klonla
git clone https://github.com/Rum-eysa/YZTA-bootcamp-Team-44
cd YZTA-bootcamp-Team-44

# Environment değişkenlerini yapılandır
cp .env.example .env

# Tüm servisleri başlat
make build && make up

# Veritabanı tablolarını oluştur
make migrate

# (İsteğe bağlı) Demo kullanıcıları yükle
make seed
```

### Erişim Noktaları

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Dokümantasyonu**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **MinIO Console**: http://localhost:9001

## Geliştirme

### Kullanılabilir Komutlar

```bash
# Servisleri başlat
make up

# Logları görüntüle
make logs

# Testleri çalıştır
make test

# Servisleri durdur
make down

# Tüm ortamı temizle
make clean

# Production deployment
make prod-up
```

Daha fazla komut için [Makefile](./Makefile) dosyasını inceleyebilirsiniz.

### Ortam Yapılandırması

Örnek ortam dosyasını kopyalayın:

```bash
cp .env.example .env
```

**Önemli üretim ayarları:**
- `JWT_SECRET`: Güçlü bir gizli anahtar (32+ karakter)
- `SUPABASE_DB_URL` veya `DB_PASSWORD`: Veritabanı bağlantısı
- `GEMINI_API_KEY`: Geçerli bir Google Gemini API anahtarı
- `MINIO_ROOT_USER` / `MINIO_ROOT_PASSWORD`: MinIO kimlik bilgileri
- `DEBUG`: `false` olarak ayarlayın
- `ENVIRONMENT`: `production` olarak ayarlayın

## Veritabanı Yönetimi

Veritabanı migration Alembic ile yönetilir:

```bash
# Yeni migration oluştur
docker-compose exec api alembic revision --autogenerate -m "açıklama"

# Migration'ları uygula
docker-compose exec api alembic upgrade head

# Bir migration geri al
docker-compose exec api alembic downgrade -1
```

## Testler

```bash
# Tüm testleri çalıştır
make test

# Coverage raporu oluştur
docker-compose exec api pytest tests/ --cov=app --cov-report=html
```

## API Dokümantasyonu

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Code Quality

### Pre-commit Hooks

```bash
pip install pre-commit
pre-commit install
```

### Manuel Linting

```bash
# Python (apps/api dizininde)
cd apps/api
black app/
isort app/
flake8 app/
mypy app/

# Frontend
cd apps/web
npm run lint
```

## Production Deployment

```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Production Kontrol Listesi

- [ ] Environment değişkenleri yapılandırıldı
- [ ] `JWT_SECRET` güçlü değerle değiştirildi
- [ ] `DEBUG` `false` olarak ayarlandı
- [ ] Database yedeği alındı
- [ ] Migration'lar uygulandı
- [ ] Tüm testler geçti
- [ ] Health check endpoint çalışıyor

## API Endpoint'leri

Tüm API route'ları `/api` prefix'i altında tanımlıdır (health hariç).

### Authentication
- `POST /api/auth/register` - Kullanıcı kaydı
- `POST /api/auth/login` - Kullanıcı girişi (JWT)
- `POST /api/auth/refresh` - Token yenileme
- `POST /api/auth/logout` - Çıkış (Redis token blacklist)

### Users
- `GET /api/users/me` - Mevcut kullanıcı profili
- `PUT /api/users/me` - Kullanıcı profili güncelleme
- `GET /api/users/{user_id}` - Kullanıcı bilgisi

### Profiles
- `PATCH /api/profiles/me` - Profil güncelleme (US-008)

### Analysis
- `POST /api/analyze` - İlan metni veya URL analizi (AI)

### Matching & Documents (Sprint 2)
- `POST /api/match` - Profil ↔ ilan eşleştirme skoru (cache'li)
- `POST /api/generate-cover-letter` - Şirkete özel önyazı üretimi (AI)
- `POST /api/generate-cv` - İlana özel PDF CV üretimi (LaTeX/Tectonic)

### Agents
- `POST /api/agents/tasks` - Agent görevi oluşturma
- `GET /api/agents/tasks/{task_id}` - Görev durumu
- `GET /api/agents/status` - Agent sistemi durumu

### Health
- `GET /health` - Health check
- `GET /health/ready` - Readiness probe

## Agent Sistemi

Sprint 1'de temel agent altyapısı ve dört AI modülü devreye alınmıştır:

- **İlan Analizi** — İş ilanındaki beceri ve deneyim beklentilerini çıkarır
- **Eşleştirme** — Aday profili ile ilan arasında uygunluk puanı hesaplar
- **CV Üretimi** — İlana özel CV oluşturur ve PDF olarak MinIO'ya kaydeder
- **Önyazı Üretimi** — Profil ve ilan bilgisine göre önyazı metni üretir

Agent görevleri `POST /api/agents/tasks` üzerinden tetiklenebilir; Gemini client rate limiting ve token tracking ile çalışır.

## Katkıda Bulunma

Katkılarınızı bekliyoruz! Lütfen yönergeler için [CONTRIBUTING.md](./CONTRIBUTING.md) dosyasını okuyun.

## Lisans

Bu proje MIT Lisansı altında lisanslanmıştır - detaylar için [LICENSE](./LICENSE) dosyasına bakın.

## Destek

Sorularınız ve desteğiniz için GitHub'da issue açabilirsiniz.

---

<div align="center">

**Built with ❤️ by YZTA Bootcamp Team 44**

[⬆ Başa Dön](#yzta-bootcamp---ai-destekli-staj-başvuru-platformu)

</div>
