# Güvenlik Checklist (US-053)

Son güncelleme: 2026-07-31

## Kimlik doğrulama / JWT

- [x] Access token: HS256, `type=access`, `jti`, Redis blacklist (logout)
- [x] Refresh token: rotation + eski `jti` blacklist; `is_active` kontrolü
- [x] `get_current_user_id`: blacklist + DB `is_active`
- [x] Frontend: 401 → `/api/auth/refresh` → retry; logout API çağrısı
- [x] Prod: `JWT_SECRET` default / kısa değerle ayağa kalkmaz (`DEBUG=false`)

## Veri izolasyonu

- [x] Listing / match / CV / önyazı: sahiplik (`created_by` / `user_id`) → 404
- [x] Profil alt kaynakları: yalnızca sahibi CRUD
- [x] `GET /api/users/{id}`: JWT + yalnızca self
- [x] `/api/agents/*`: JWT + task sahipliği
- [x] MinIO bucket private; CV/avatar tarayıcıya MinIO/presigned URL ile verilmez
- [x] `GET /api/documents/{id}/file` ve avatar file: JWT + sahiplik; anonim/başka kullanıcı 401/404

## Prompt injection

- [x] `extra_prompt` delimiter + yok say talimatı
- [x] Profil / ilan / matching JSON `wrap_untrusted_block`
- [x] `document_language` allowlist (`tr`|`en`)

## Ağ / abuse

- [x] SSRF: private/loopback/link-local/metadata engeli, redirect limiti
- [x] Rate limit (Redis): login/register, analyze, match, generate-*, process
- [x] Gemini uygulama kotası (dakikalık; test ortamında no-op)

## Audit / gözlemlenebilirlik

- [x] Structured audit: login fail, analyze, match, generate-cv, generate-cover-letter, profile PATCH, process
- [x] Loglarda token / parola yazılmaz

## Regression

- [x] `apps/api/tests/test_security_hardening.py`
- [x] Mevcut IDOR / auth testleri CI’da çalışır
