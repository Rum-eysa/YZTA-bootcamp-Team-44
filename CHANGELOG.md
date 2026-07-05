# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Sprint-1 AI agents: listing analysis, matching, CV generation, cover letter
- MinIO storage integration for CV PDFs
- Gemini client with rate limiting and token tracking
- `POST /api/analyze` endpoint and agent-oriented DB schema
- `PATCH /api/profiles/me` profile alias (US-008)
- Seed script for demo data (`make seed`)

### Changed
- **US-004 decision:** Embedded Tectonic in API Docker image; standalone `apps/compiler/` removed
- Auth routes under `/api` prefix with logout (Redis token blacklist)
- Database schema: `job_listings`, `matches`, `documents` (replaces `applications` CRUD)

### Removed
- Standalone compiler microservice and `/documents/compile` proxy
- Applications CRUD API (`/applications`)

### Added (initial)
- Initial project structure with FastAPI backend和 Next.js frontend
- PostgreSQL database with SQLAlchemy ORM
- Redis caching layer
- JWT authentication system
- Google Gemini AI integration for application analysis
- Docker and Docker Compose configuration
- Health check endpoints
- Structured logging with request ID tracking
- Security middleware (CORS, GZip, TrustedHost, security headers)
- Exception handling with custom error codes
- Pydantic schemas for request/response validation
- Testing setup with pytest
- CI/CD pipeline with GitHub Actions
- Pre-commit hooks for code quality
- Docker ignore files for optimized builds
- License file (MIT)
- Project documentation

### Security
- Added security headers middleware
- JWT-based authentication
- Password hashing with bcrypt
- CORS configuration
- Trusted host middleware for production

## [1.0.0] - 2024-06-30

### Added
- Initial release
