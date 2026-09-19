run:
	uvicorn app.api:app --reload

test:
	pytest -q

docker:
	docker compose -f deploy/docker-compose.yml up --build
