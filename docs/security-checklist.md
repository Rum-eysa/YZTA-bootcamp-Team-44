# Security Checklist

This checklist summarizes the current security hardening controls implemented for US-053.

## Access control and IDOR protection
- Verify that listings are accessible only by their owner.
- Verify that listing edit and analysis operations return `404` for unauthorized users.
- Verify that profile resources are accessible only by the authenticated owner.
- Verify that listing-related subresources (matches, CVs, cover letters) load through the authenticated user context.

## Audit logging
- Structured audit logs are emitted for failed login attempts.
- Structured audit logs are emitted for profile patch operations.
- Structured audit logs are emitted for match generation.
- Structured audit logs are emitted for CV generation.
- Structured audit logs are emitted for cover letter generation.

## Rate limiting and brute-force protection
- Login endpoint is rate limited.
- Registration endpoint is rate limited.
- Match generation endpoint is rate limited.
- CV generation endpoint is rate limited.
- Cover letter generation endpoint is rate limited.

## Defense-in-depth and database-level controls
- Row-Level Security is enabled for profile expansion tables.
- The app documentation notes that service_role bypass must not be used from public-facing endpoints.
- Security headers and CORS restrictions are applied at the FastAPI middleware layer.

## Testing
- Regression tests are present for listing ownership isolation.
- Regression tests verify `auth_login_failed` audit logging.
- Regression tests verify audit-event emission for profile patch, match, CV, and cover letter generation.

## Notes
- `apps/api/tests/test_security_hardening.py` contains the new regression coverage.
- `docs/security-checklist.md` is the canonical project security checklist for US-053.
