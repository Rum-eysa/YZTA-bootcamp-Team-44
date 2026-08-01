# Katkı Rehberi — CareerTrack

Katkılarınız için teşekkürler. Bu rehber, lokal kurulumdan pull request’e kadar izlenecek adımları özetler.

## Hızlı başlangıç

```bash
git clone https://github.com/Rum-eysa/YZTA-bootcamp-Team-44
cd YZTA-bootcamp-Team-44
cp .env.example .env

make build && make up
make migrate
make seed          # isteğe bağlı demo verisi
```

- Frontend: http://localhost:3000  
- API docs: http://localhost:8000/docs  
- Detaylı komutlar: [Makefile](./Makefile) · canlı ortam: [docs/deploy.md](./docs/deploy.md)

## Branch ve PR akışı

1. `main`’den güncel branch açın:
   ```bash
   git checkout main && git pull
   git checkout -b feat/kisa-aciklama
   ```
2. Değişikliği yapın, test edin, commit atın.
3. Branch’i push edip GitHub’da Pull Request açın.
4. En az **1 onay** sonrası merge edilir.

Branch adı örnekleri: `feat/...`, `fix/...`, `docs/...`

## Commit mesajı

```
<type>: <kısa açıklama>
```

| Type | Kullanım |
| --- | --- |
| `feat` | Yeni özellik |
| `fix` | Hata düzeltme |
| `docs` | Dokümantasyon |
| `refactor` | Davranış değiştirmeyen yeniden yazım |
| `test` | Test ekleme / güncelleme |
| `chore` | Build, bağımlılık, CI |

Örnek: `feat: add guest ATS check endpoint`

## Kod stili

**Backend (`apps/api`):**

```bash
cd apps/api
black app/
isort app/
flake8 app/
mypy app/
```

**Frontend (`apps/web`):**

```bash
cd apps/web
npm run lint
```

## Test

```bash
make test
# veya tek dosya:
docker-compose exec -e PYTHONPATH=/app api pytest tests/test_ats_check.py -v
```

- Yeni davranış için mümkünse test ekleyin.
- Agent / güvenlik değişikliklerinde mevcut CI coverage gate’ini bozmayın.

## PR kontrol listesi

- [ ] Branch adı ve commit mesajları anlaşılır
- [ ] Lint / format geçiyor
- [ ] İlgili testler çalışıyor (`make test`)
- [ ] Gerekirse README veya `docs/deploy.md` güncellendi
- [ ] `.env` / secret commit edilmedi; yeni env varsa `.env.example` güncellendi

## Proje yapısı (kısa)

```
apps/api/app/     # FastAPI: routes, agents, services, schemas
apps/web/app/     # Next.js App Router: landing, profile, apply, listings
docs/             # Deploy ve sprint görselleri
```

Kanonik ilan sayfası: `/listings/{listingId}`. Misafir ATS: landing → `POST /api/ats-check`.

## Güvenlik

- `.env` asla commit edilmez
- Kullanıcı girdisini doğrulayın; sahiplik kontrollerini atlamayın
- Production’da güçlü `JWT_SECRET`, `DEBUG=false`

## Sorun / özellik bildirimi

GitHub Issues kullanın. Bug için: beklenen / gerçekleşen davranış, adımlar, ortam (lokal veya canlı URL).

Sorular için issue veya PR discussion açabilirsiniz.
