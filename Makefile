.PHONY: static
static: format lint mypy

.PHONY: format
format:
	isort rsclimatelab tests

.PHONY: lint
lint:
	flake8 rsclimatelab tests

.PHONY: mypy
mypy:
	mypy rsclimatelab tests

.PHONY: test
test:
	pytest --cov=rsclimatelab --cov-branch tests

.PHONY: ci
ci: format lint mypy test
