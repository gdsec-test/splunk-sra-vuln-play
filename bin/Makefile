pkg_root := $(shell pwd)


.PHONY: all
all: .venv

.PHONY: isort
isort: .venv/bin/isort
	.venv/bin/isort -rc ./test --atomic --diff

.PHONY: flake8
flake8: .venv/bin/flake8
	.venv/bin/flake8 --config ./.flake8 test

.PHONY: local
local: .venv
	.venv/bin/python3.7 main.py --local

.PHONY: test
test: .venv/bin/py.test
	.venv/bin/py.test -v test/

.PHONY: testcov
testcov: .venv/bin/py.test
	.venv/bin/py.test --cov --cov-config=.coveragerc --cov-branch --tb=short --cov-report term-missing

.PHONY: tools
tools: isort flake8
	.venv/bin/py.test -v test/

.venv:
	python3 -m virtualenv .venv
	.venv/bin/pip install --upgrade pip
	.venv/bin/pip install -r requirements.txt

.venv/bin/py.test: | .venv
	.venv/bin/pip install pytest
	.venv/bin/pip install pytest-cov

.venv/bin/%: | .venv
	.venv/bin/pip install $(@F)

clean:
	test ! -d .pytest_cache || rm -rf .pytest_cache
	find . -regex ".*\.pyc$$" -type f -exec rm {} \;
	find . -name __pycache__ -type d -prune -exec rm -rf {} \;

clean-all: clean
	test ! -d .venv || rm -rf .venv