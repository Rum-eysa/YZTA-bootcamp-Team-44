# YZTA Bootcamp - AI Destekli Staj Başvuru Platformu

<div align="center">

![YZTA Bootcamp](https://img.shields.io/badge/YZTA-Bootcamp-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green)
![Next.js](https://img.shields.io/badge/Next.js-14.2-black)
![Python](https://img.shields.io/badge/Python-3.11-blue)
![License](https://img.shields.io/badge/License-MIT-yellow)

**Kurumsal AI destekli staj başvuru yönetim platformu**

[Özellikler](#-özellikler) • [Hızlı Başlangıç](#-hızlı-başlangıç) • [Mimari](#-mimari) • [API Dokümantasyonu](#-api-dokümantasyonu) • [Katkıda Bulunma](#-katkıda-bulunma)

</div>

---

YZTA Bootcamp, yapay zeka destekli akıllı başvuru analizi için üretime hazır bir staj başvuru platformudur. Modern teknolojilerle inşa edilmiş; ölçeklenebilirlik, güvenlik ve bakım için sektörün en iyi uygulamalarını takip eder.

## 👥 Takım İsmi

YZTA Bootcamp Team 44

## 🧑‍🤝‍🧑 Takım Rolleri

| Rol | Kişi | GitHub |
|-----|------|--------|
| Product Owner | Rum-eysa | [@Rum-eysa](https://github.com/Rum-eysa) |
| Scrum Master | Serkan0YLDZ | [@Serkan0YLDZ](https://github.com/Serkan0YLDZ) |
| Developer | zeynepmaidedemir | [@zeynepmaidedemir](https://github.com/zeynepmaidedemir) |
| Developer | lizlavigne | [@lizlavigne](https://github.com/lizlavigne) |

## 📌 Ürün İsmi

YZTA Bootcamp - AI Destekli Staj Başvuru Platformu

## 📝 Ürün Açıklaması

Bu proje, staj başvurularının daha hızlı, daha adil ve daha verimli bir şekilde değerlendirilmesini sağlamak amacıyla yapay zeka destekli bir çözüm sunar. Adayların başvuru metinlerini analiz ederek, kurumların değerlendirme sürecini kolaylaştırmayı ve insan kaynak süreçlerini desteklemeyi hedefler.

## 💡 Problem Tanımı

Staj başvuruları genellikle yüksek başvuru sayısı, manuel değerlendirme ve zaman kısıtları nedeniyle verimsiz bir sürece dönüşebilir. Bu proje ile başvuruların içerik analizi yapılarak ön değerlendirme süreci hızlandırılır, adayların uygunluğu daha net şekilde karşılaştırılabilir ve karar alma süreci desteklenir.

## 📈 İş Değeri

- Başvuru değerlendirme süresini azaltır.
- Değerlendiricilere daha tutarlı bir ön analiz sunar.
- İnsan kaynak süreçlerini daha verimli hale getirir.
- Aday deneyimini daha şeffaf ve anlaşılır kılar.

## ✨ Ürün Özellikleri

- **🤖 AI Destekli Analiz** - Google Gemini ile akıllı başvuru değerlendirmesi.
- **🔐 Güvenli Kimlik Doğrulama** - JWT tabanlı kimlik doğrulama ve bcrypt şifreleme.
- **📝 Başvuru Yönetimi** - Tam staj başvuru yaşam döngüsü yönetimi.
- **⚡ Yüksek Performans** - Redis önbellekleme katmanı ile asenkron işleme.
- **📊 İzlenebilirlik** - Yapılandırılmış loglama ve istek takibi.
- **🛡️ Kurumsal Güvenlik** - CORS, hız sınırlama, güvenlik başlıkları ve giriş doğrulama.
- **🧪 Kapsamlı Testler** - Yüksek kapsamlı birim ve entegrasyon testleri.
- **🚀 Sürekli Entegrasyon / Dağıtım** - GitHub Actions ile otomatik test ve dağıtım.
- **🔄 Veritabanı Göçleri** - Alembic ile versiyon kontrollü şema değişiklikleri.
- **🎨 Modern Arayüz** - TailwindCSS ve Next.js 14 ile duyarlı kullanıcı arayüzü.

## 🎯 Hedef Kitle

- Öğrenciler
- Staj veren şirketler
- Bootcamp ve kariyer geliştirme programları
- İnsan kaynak ve işe alım ekipleri

## 📋 Ürün Backlog'u

Proje backlog bilgileri GitHub Projects üzerinden yönetilmektedir:

- [GitHub Projects Backlog](https://github.com/users/Rum-eysa/projects/6/views/1?groupedBy%5BcolumnId%5D=364119553)
- Sprint planları ve görev takibi burada güncellenmektedir.

## 🔁 Sprint Planı

### Sprint 1
- Temel kullanıcı akışları ve sistem mimarisinin kurulması
- Başvuru oluşturma ve görüntüleme işlevlerinin geliştirilmesi
- İlk test senaryolarının hazırlanması

### Sprint 2
- AI destekli analiz akışının entegrasyonu
- Kullanıcı deneyimini iyileştiren temel arayüz güncellemeleri
- Geliştirme ve test süreçlerinin güçlendirilmesi

### Sprint 3
- Performans iyileştirmeleri ve hata düzeltmeleri
- Kullanıcı geri bildirimlerine göre iyileştirmeler
- Son kullanıcıya hazır hale getirme çalışmaları

## 🏗️ Mimari

```
.
├── apps/
│   ├── api/                         # FastAPI Backend Service
│   │   ├── app/
│   │   │   ├── main.py              # Application entry point
│   │   │   ├── config.py            # Configuration management
│   │   │   ├── models.py            # SQLAlchemy ORM models
│   │   │   ├── database.py          # Database connection
│   │   │   ├── exceptions.py        # Custom exceptions
│   │   │   ├── middleware.py        # Custom middleware
│   │   │   ├── logging_config.py    # Logging configuration
│   │   │   ├── routes/              # API endpoints
│   │   │   │   ├── auth.py          # Authentication endpoints
│   │   │   │   ├── users.py         # User management
│   │   │   │   ├── applications.py  # Application CRUD
│   │   │   │   └── health.py        # Health checks
│   │   │   ├── services/            # Business logic layer
│   │   │   │   ├── auth.py          # Authentication service
│   │   │   │   ├── user.py          # User service
│   │   │   │   └── application.py   # Application service
│   │   │   └── schemas/             # Pydantic schemas
│   │   │       ├── user.py
│   │   │       ├── application.py
│   │   │       └── base.py
│   │   ├── tests/                   # Test suite
│   │   ├── alembic/                 # Database migrations
│   │   ├── requirements.txt         # Python dependencies
│   │   ├── Dockerfile               # Production image
│   │   └── alembic.ini              # Alembic config
│   │
│   └── web/                         # Next.js Frontend Service
│       ├── app/                     # App Router
│       │   ├── page.tsx             # Landing page
│       │   ├── layout.tsx           # Root layout
│       │   └── globals.css          # Global styles
│       ├── lib/                     # Utilities
│       │   ├── api.ts               # API client
│       │   └── utils.ts             # Helper functions
│       ├── components/              # React components (future)
│       ├── public/                  # Static assets
│       ├── package.json             # Node dependencies
│       ├── tailwind.config.ts       # Tailwind config
│       └── Dockerfile               # Production image
│
├── .github/                         # GitHub configuration
│   └── workflows/                   # CI/CD pipelines
│       └── ci.yml                   # Main CI workflow
│
├── docker-compose.yml               # Development environment
├── docker-compose.prod.yml          # Production environment
├── Makefile                         # Command shortcuts
├── pyproject.toml                   # Python project config
├── .pre-commit-config.yaml          # Pre-commit hooks
├── .editorconfig                    # Editor settings
├── .dockerignore                    # Docker ignore files
├── .gitignore                       # Git ignore rules
├── LICENSE                          # MIT License
├── README.md                        # This file
├── CHANGELOG.md                     # Version history
└── CONTRIBUTING.md                  # Contribution guidelines
```

### Teknoloji Stack

| Katman | Teknoloji | Amaç |
| --- | --- | --- |
| **Frontend** | Next.js 14, React 18, TypeScript, TailwindCSS | Modern, SEO dostu arayüz |
| **Backend** | FastAPI, SQLAlchemy 2.0, Pydantic V2 | Yüksek performanslı async API |
| **Veritabanı** | PostgreSQL 15 | Ana veri depolama |
| **Önbellek** | Redis 7 | Önbellekleme ve oturum yönetimi |
| **AI/ML** | Google Gemini | Başvuru analizi |
| **Altyapı** | Docker, Docker Compose | Konteyner orkestrasyonu |
| **Test** | Pytest, pytest-asyncio, Coverage | Kapsamlı testler |
| **CI/CD** | GitHub Actions | Otomatik iş akışları |
| **Kod Kalitesi** | Black, isort, flake8, mypy, pre-commit | Linting ve formatlama |
| **Gelecek** | Agent Sistemi (LangChain/CrewAI) | Otomatik iş akışı yönetimi |

## 🚀 Hızlı Başlangıç

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
cp .env.example .env.local

# Tüm servisleri başlat
make build && make up
```

### Erişim Noktaları

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Dokümantasyonu**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🛠️ Geliştirme

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
cp .env.example .env.local
```

**Önemli üretim ayarları:**
- `JWT_SECRET`: Güçlü bir gizli anahtar (32+ karakter)
- `DB_PASSWORD`: Güvenli veritabanı parolası
- `DEBUG`: `false` olarak ayarlayın
- `ENVIRONMENT`: `production` olarak ayarlayın
- `GEMINI_API_KEY`: Geçerli bir Google Gemini API anahtarı

## 🗄️ Veritabanı Yönetimi

Veritabanı göçleri Alembic ile yönetilir:

```bash
# Yeni migration oluştur
docker-compose exec api alembic revision --autogenerate -m "açıklama"

# Migration'ları uygula
docker-compose exec api alembic upgrade head

# Bir migration geri al
docker-compose exec api alembic downgrade -1
```

## 🧪 Testler

```bash
# Tüm testleri çalıştır
make test

# Coverage raporu oluştur
docker-compose exec api pytest tests/ --cov=app --cov-report=html
```

## 📝 API Dokümantasyonu

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔧 Kod Kalitesi

### Pre-commit Hookları

```bash
pip install pre-commit
pre-commit install
```

### Manuel Linting

```bash
# Python
black app/
isort app/
flake8 app/
mypy app/

# Frontend
cd apps/web
npm run lint
```

## 🐳 Üretim Dağıtımı

```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Üretim Kontrol Listesi

- [ ] Ortam değişkenleri yapılandırıldı
- [ ] `JWT_SECRET` güçlü bir değerle değiştirildi
- [ ] `DEBUG` `false` olarak ayarlandı
- [ ] Veritabanı yedeği alındı
- [ ] Göçler uygulandı
- [ ] Tüm testler geçti
- [ ] Sağlık kontrol endpoint'i çalışıyor

## 📚 API Endpoint'leri

### Kimlik Doğrulama
- `POST /auth/register` - Kullanıcı kaydı
- `POST /auth/login` - Kullanıcı girişi
- `POST /auth/refresh` - Token yenileme

### Kullanıcılar
- `GET /users/me` - Mevcut kullanıcı profili
- `PUT /users/me` - Kullanıcı profili güncelleme
- `GET /users/{user_id}` - Kullanıcı bilgisi

### Başvurular
- `POST /applications` - Başvuru oluşturma
- `GET /applications` - Başvuru listesi
- `GET /applications/{id}` - Başvuru detayları
- `PUT /applications/{id}` - Başvuru güncelleme
- `POST /applications/{id}/analyze` - AI analizi

### Sağlık
- `GET /health` - Health check
- `GET /health/ready` - Readiness probe

### Ajanlar (Gelecek Entegrasyon)
- `POST /agents/tasks` - Agent görevi oluşturma
- `GET /agents/tasks/{task_id}` - Görev durumu
- `GET /agents/status` - Agent sistemi durumu

## 🤖 Gelecek: Ajan Sistemi Entegrasyonu

Mimari, AI ajan sistemlerinin gelecekte otomatik iş akışı yönetimi için entegre edilmesine uygun şekilde tasarlanmıştır:

**Planlanan Özellikler:**
- **LangChain/CrewAI Entegrasyonu** - Çok ajanlı iş akışları
- **Otomatik Başvuru İşleme** - Akıllı yönlendirme ve sınıflandırma
- **Akıllı Bildirimler** - Bağlam bilincine sahip uyarılar
- **Karar Desteği** - AI destekli öneriler
- **Görev Otomasyonu** - Otomatik takip ve planlama

**Hazır Mimari Yapı:**
- Ajan entegrasyonu için servis katmanı soyutlaması
- Olay tabanlı mimari desteği
- Redis ile asenkron işleme kapasitesi
- Ajan eklemeyi kolaylaştıran modüler yapı

## 🤝 Katkıda Bulunma

Katkılarınızı bekliyoruz! Lütfen yönergeler için [CONTRIBUTING.md](./CONTRIBUTING.md) dosyasını okuyun.

## 📜 Lisans

Bu proje MIT Lisansı altında lisanslanmıştır - detaylar için [LICENSE](./LICENSE) dosyasına bakın.

## 📞 Destek

Sorularınız ve desteğiniz için GitHub'da issue açabilirsiniz.

---

<div align="center">

**Built with ❤️ by YZTA Bootcamp Team 44**

[⬆ Başa Dön](#yzta-bootcamp---ai-destekli-staj-başvuru-platformu)

</div>
