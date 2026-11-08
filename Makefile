.PHONY: build test lint cli shell clean

build:
	docker compose build

test:
	docker compose run --rm test

lint:
	docker compose run --rm lint

cli:
	docker compose run --rm cli $(ARGS)

shell:
	docker compose run --rm shell

clean:
	docker compose down --rmi local --volumes --remove-orphans
