.PHONY: install test lint type-check format docs serve-docs clean all

install:
	uv sync --all-extras

test:
	uv run pytest tests/ -v

lint:
	uv run ruff check src/ tests/
	uv run ruff format --check src/ tests/

format:
	uv run ruff format src/ tests/
	uv run ruff check --fix src/ tests/

type-check:
	uv run mypy src/

docs:
	uv run mkdocs build

serve-docs:
	uv run mkdocs serve

clean:
	rm -rf dist/ build/ *.egg-info .pytest_cache .mypy_cache .ruff_cache site/
	find . -type d -name __pycache__ -exec rm -rf {} +

all: lint type-check test
