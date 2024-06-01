.PHONY: static
static: format lint mypy

.PHONY: format
format:
	isort rs-climate-lab tests

.PHONY: lint
lint:
	flake8 rs-climate-lab tests

.PHONY: mypy
mypy:
	mypy rs-climate-lab tests

.PHONY: test
test:
	pytest --cov=rs-climate-lab --cov-branch tests

.PHONY: ci
ci: format lint mypy test
