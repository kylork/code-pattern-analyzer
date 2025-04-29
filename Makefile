.PHONY: install test run docker docker-build docker-run clean

# Install in development mode
install:
	pip install -e .

# Run tests
test:
	python -m unittest discover tests

# Run the demo
run:
	python run_demo.py

# Run the CLI tool
cli:
	code-pattern

# Run the CLI tool with a specific command
# Usage: make analyze FILE=sample.py
analyze:
	code-pattern analyze --file $(FILE)

# Build Docker image
docker-build:
	docker build -t code-pattern-analyzer .

# Run Docker container
# Usage: make docker-run CMD="analyze --file /code/sample.py"
docker-run:
	docker run -v $(PWD)/sample-code:/code -w /code code-pattern-analyzer $(CMD)

# Run with docker-compose
docker:
	docker-compose up --build

# Clean up
clean:
	rm -rf __pycache__ build dist *.egg-info
	find . -name "*.pyc" -delete