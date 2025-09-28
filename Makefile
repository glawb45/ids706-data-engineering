install:
	pip install --upgrade pip &&\
		pip install -r requirements.txt

format:
	black *.py

test:
	python -m pytest -vv --cov=hello test_*.py

clean:
	rm -rf __pycache__ .pytest_cache .coverage

flake8:
	flake8 --ignore=E203,W503,E501 .

all: install format test