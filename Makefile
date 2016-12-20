.PHONY: install upgrade lint coverage travis docs

install:
	pip install -r requirements-dev.txt
	pip install -e .

upgrade:
	pip install -r requirements-dev.txt -U
	pip install -e . -U

lint:
	flake8

isort:
	isort --check-only --recursive --diff nomad tests

coverage:
	py.test --cov-report term-missing --cov nomad

spec:
	py.test --spec -p no:sugar
