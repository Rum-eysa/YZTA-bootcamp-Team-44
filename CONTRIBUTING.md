# Contributing Guide

Projeye katkı sağladığınız için teşekkürler! Aşağıdaki kuralları lütfen takip edin.

## 🎯 Pull Request Process

1. **Fork & Branch**: `main` 'den yeni branch oluştur
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Commit**: Clear ve descriptive messages kullan
   ```bash
   git commit -m "feat: add authentication endpoints"
   git commit -m "fix: handle database connection errors"
   git commit -m "docs: update API documentation"
   ```

3. **Push & PR**: 
   - Branch'i push et
   - Detailed PR description yaz
   - Self-review yap

4. **Review & Merge**: Minimum 1 approval gerekli

## 📝 Commit Message Format

```
<type>: <subject>

<body (opsiyonel)>

<footer (opsiyonel)>
```

**Types:**
- `feat`: Yeni feature
- `fix`: Bug fix
- `docs`: Dokumentasyon
- `style`: Code style (formatting, semicolons, etc.)
- `refactor`: Code refactoring
- `test`: Test ekle/düzenle
- `chore`: Build, dependencies, etc.

**Örnek:**
```
feat: implement user authentication with JWT

- Add login endpoint
- Add token refresh mechanism
- Add authentication middleware

Closes #123
```

## 🏗️ Code Style

### Backend (Python)

```bash
# Format
black apps/api/

# Lint
flake8 apps/api/

# Type check
mypy apps/api/app/

# Sort imports
isort apps/api/
```

### Frontend (TypeScript)

```bash
# Lint
pnpm lint

# Format
pnpm format  # (kurulması gerekirse Prettier)
```

## 🧪 Testing Requirements

- Backend: `make test` hepsini pass etmeli
- Yeni feature için yeni test ekle
- Coverage minimum %80 olmalı

```bash
# Local test
make test

# Specific test
docker-compose exec api pytest tests/test_api.py::test_health -v
```

## 📋 PR Checklist

PR açmadan önce kontrol et:

- [ ] Branch adı descriptive (`feature/x`, `fix/x`)
- [ ] Commits clear ve logically organized
- [ ] Code formatı doğru (`black`, `flake8`)
- [ ] Tests yazıldı ve hepsi pass ediyor
- [ ] Documentation güncellenmiş
- [ ] No hardcoded secrets veya sensitive data
- [ ] `.env.example` güncellenmiş (gerekirse)

## 🔒 Security Guidelines

1. **Never commit secrets**: `.env.local` hiçbir zaman git'e girmesin
2. **Validate inputs**: Tüm external inputs validate et
3. **Use prepared statements**: SQL injection'ı önle
4. **HTTPS in production**: Always use HTTPS
5. **Rate limiting**: API endpoints'e rate limiting ekle

## 🐛 Bug Reports

Issues açarken şunları include et:

```markdown
## Açıklama
Ne olması gerekiyordu ve ne oldu?

## Reproduce Steps
1. Step 1
2. Step 2
3. Step 3

## Expected vs Actual
- Expected: X
- Actual: Y

## Environment
- OS: Windows/Mac/Linux
- Docker version: X.X.X
- Git commit: abc123
```

## 💡 Feature Requests

```markdown
## Açıklama
Yeni feature'ın açıklaması

## Use Case
Bu feature neden gerekli?

## İmplementasyon önerisi
Nasıl implement edilebilir? (opsiyonel)
```

## 🚀 Development Workflow

```bash
# 1. Clone
git clone https://github.com/Rum-eysa/YZTA-bootcamp-Team-44
cd YZTA-bootcamp-Team-44

# 2. Setup
cp .env.example .env.local
make build

# 3. Develop
make up
make logs

# 4. Test
make test

# 5. Format & Lint
cd apps/api && black . && flake8 . && mypy app/
cd ../web && pnpm lint

# 6. Commit & Push
git add .
git commit -m "type: description"
git push origin feature/your-feature

# 7. Create PR on GitHub
```

## 📚 Project Structure Best Practices

### Backend (apps/api/)

```
app/
├── routes/          # API endpoints (organize by domain)
│   ├── auth.py
│   ├── users.py
│   └── applications.py
├── schemas/         # Pydantic models (requests/responses)
├── services/        # Business logic
├── models.py        # Database models
├── database.py      # Connection setup
└── config.py        # Settings
```

### Frontend (apps/web/)

```
app/
├── (routes)/        # Next.js route groups
│   ├── dashboard/
│   ├── auth/
│   └── applications/
├── components/      # Reusable components
├── hooks/          # Custom React hooks
├── lib/            # Utilities
└── types/          # TypeScript types
```

## 🤝 Code Review Standards

Reviewing sırasında:

1. **Functionality**: Kod intended behavior'ı implement ediyor mu?
2. **Code Quality**: Clean, readable, maintainable mi?
3. **Performance**: N+1 queries, unnecessary loops, memory leaks var mı?
4. **Security**: Input validation, SQL injection, XSS var mı?
5. **Tests**: Adequate coverage var mı?
6. **Documentation**: Comments ve docs gerekli mi?

## 📞 Questions?

- GitHub Issues'de soru aç
- Pull request'te discussion başlat
- Team'le iletişime geç

---

**Happy contributing! 🚀**
