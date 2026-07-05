.PHONY: up down build logs logs-api logs-web test test-cov ps restart clean migrate seed shell-api shell-web help

## ─── Local Development ───────────────────────────────────────────────────────

up: ## Tüm servisleri arka planda başlat
	docker-compose up -d

down: ## Tüm servisleri durdur
	docker-compose down

build: ## Image'ları yeniden build edip başlat
	docker-compose up -d --build

restart: ## Tüm servisleri yeniden başlat
	docker-compose restart

ps: ## Çalışan container'ları listele
	docker-compose ps

## ─── Logs ────────────────────────────────────────────────────────────────────

logs: ## Tüm servislerin log'larını izle
	docker-compose logs -f

logs-api: ## Sadece API log'larını izle
	docker-compose logs -f api

logs-web: ## Sadece Web log'larını izle
	docker-compose logs -f web

## ─── Testing ─────────────────────────────────────────────────────────────────

test: ## API testlerini çalıştır
	docker-compose exec -e PYTHONPATH=/app api pytest tests/ -v

test-cov: ## Testleri coverage raporu ile çalıştır
	docker-compose exec -e PYTHONPATH=/app api pytest tests/ -v --cov=app --cov-report=term-missing

## ─── Database ────────────────────────────────────────────────────────────────

migrate: ## Alembic migration'larını uygula
	docker-compose exec -e PYTHONPATH=/app api alembic upgrade head

migrate-create: ## Yeni migration dosyası oluştur (msg= ile kullan)
	docker-compose exec -e PYTHONPATH=/app api alembic revision --autogenerate -m "$(msg)"

seed: ## Demo verisi yükle (US-010)
	docker-compose exec -e PYTHONPATH=/app api python scripts/seed_database.py

## ─── Shell Access ────────────────────────────────────────────────────────────

shell-api: ## API container'ına bağlan
	docker-compose exec api bash

shell-web: ## Web container'ına bağlan
	docker-compose exec web sh

shell-db: ## PostgreSQL shell'ine bağlan
	docker-compose exec postgres psql -U yzta_user -d yzta_bootcamp

## ─── Production ──────────────────────────────────────────────────────────────

prod-up: ## Production container'larını başlat
	docker-compose -f docker-compose.prod.yml up -d

prod-down: ## Production container'larını durdur
	docker-compose -f docker-compose.prod.yml down

prod-build: ## Production image'larını build et
	docker-compose -f docker-compose.prod.yml build

## ─── Cleanup ─────────────────────────────────────────────────────────────────

clean: ## Container + volume'ları temizle (veri silinir!)
	docker-compose down -v

clean-all: ## Container + volume + image'ları temizle
	docker-compose down -v --rmi local

## ─── Help ─────────────────────────────────────────────────────────────────────

help: ## Bu yardım mesajını göster
	@echo ""
	@echo "  YZTA Bootcamp — Makefile Komutları"
	@echo "  ─────────────────────────────────────────────"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}'
	@echo ""
