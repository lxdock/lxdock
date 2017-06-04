.PHONY: install upgrade lint coverage travis docs

install:
	pip install -r requirements-dev.txt
	# Temporary while we need a dev version of pylxd
	pip install --process-dependency-links -e .

upgrade:
	pip install -r requirements-dev.txt -U
	# Temporary while we need a dev version of pylxd
	pip install --process-dependency-links -e . -U

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
