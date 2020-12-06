SHELL := /bin/bash
ifndef VERBOSE
.SILENT:
endif

default:
	@echo "Usage:"
	@echo "  make test           | run test suite"
	@echo "  make lint           | run linters"
	@echo "  make black          | formats code using black"
	@echo "  make isort          | sorts import"

.PHONY: black
black:
	poetry run black ./*.py year*/day*/*.py

.PHONY: isort
isort:
	poetry run isort ./*.py year*/day*/*.py

.PHONY: flake8
flake8:
	poetry run flake8 ./*.py year*/day*/*.py

.PHONY: mypy
mypy:
	poetry run mypy ./*.py

lint: flake8 mypy

.PHONY: pytest
pytest:
	poetry run pytest tests -v

test: pytest
tests: test
