.PHONY: test-setup install spec test upgrade lint coverage isort travis docs

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

test-setup:
	sudo apt-get update -q
	sudo apt-get remove -qy lxd lxd-client
	sudo apt-get -y install snapd
	sudo snap install lxd
	sudo snap start lxd
	while [ ! -S /var/snap/lxd/common/lxd/unix.socket ]; do \
		sleep 0.5; \
	done
	sudo lxd --version
	sudo lxd init --auto
	sudo lxc network create lxdbr0 ipv6.address=none ipv4.address=10.0.3.1/24 ipv4.nat=true
	sudo lxc network attach-profile lxdbr0 default eth0
	ssh-keygen -t rsa -b 2048 -f ~/.ssh/id_rsa -P ""

travis: install lint isort coverage

docs:
	cd docs && rm -rf _build && make html
