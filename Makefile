.PHONY: up down build logs test ps restart clean build-compiler compile-test

up:
	docker-compose up -d

down:
	docker-compose down

build:
	docker-compose up -d --build

build-compiler:
	docker-compose build compiler

compile-test:
	docker-compose run --rm --entrypoint ./scripts/smoke-test.sh compiler

logs:
	docker-compose logs -f

ps:
	docker-compose ps

restart:
	docker-compose restart

test:
	docker-compose exec api pytest tests/ -v

prod-up:
	docker-compose -f docker-compose.prod.yml up -d

prod-down:
	docker-compose -f docker-compose.prod.yml down

clean:
	docker-compose down -v
