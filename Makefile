.phony: all lint test

all: lint test

lint: 
	flake8 .
	black --check .
	mypy .
	pydocstyle .

test:
	pytest tests
