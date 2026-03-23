generate:
	alembic revision --autogenerate -m "$(name)"

migrate:
	alembic upgrade head