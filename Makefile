.PHONY: install spec upgrade lint coverage isort travis docs

install:
	pip install -r requirements-dev.txt
	pip install -e .

upgrade:
	pip install -r requirements-dev.txt -U
	pip install -e . -U

lint:
	flake8

isort:
	isort --check-only --recursive --diff lxdock tests

coverage:
	py.test --cov-report term-missing --cov lxdock

spec:
	py.test --spec -p no:sugar

travis: install lint isort coverage

docs:
	cd docs && rm -rf _build && make html
