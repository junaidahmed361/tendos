.PHONY: install test test-unit test-integration lint format typecheck security coverage clean all pre-commit

install:
	uv sync --all-extras

test:
	uv run pytest tests/ -v

test-unit:
	uv run pytest tests/unit -v -m unit

test-integration:
	uv run pytest tests/integration -v -m integration

lint:
	uv run ruff check src/ tests/

format:
	uv run ruff format src/ tests/

typecheck:
	uv run mypy src/tendos

security:
	uv run bandit -r src/tendos -c pyproject.toml

coverage:
	uv run pytest --cov=tendos --cov-report=html

clean:
	rm -rf dist build *.egg-info .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage coverage.xml

all: lint typecheck security test

pre-commit:
	uv run pre-commit run --all-files
