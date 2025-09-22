install:
	pip install --upgrade pip &&\
		pip install -r requirements.txt

format:
	black *.py

test:
	python -m pytest -vv --cov=hello test_*.py

clean:
	rm -rf __pycache__ .pytest_cache .coverage

all: install format test