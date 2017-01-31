VENV=./ve
PYTHON=$(VENV)/bin/python
PIP=$(VENV)/bin/pip
COVERAGE=$(VENV)/bin/coverage
FLAKE8=$(VENV)/bin/flake8
TOX=$(VENV)/bin/tox
PROJECT=rssfeed

.PHONY: check coverage test tox venv

help:
	@echo  "usage: make <target>"
	@echo  "Targets:"
	@echo  "    up      Updates dependencies"
	@echo  "    deps    Ensure dev dependencies are installed"
	@echo  "    check	Checks that build is sane"
	@echo  "    lint	Reports pylint violations"
	@echo  "    test	Runs all tests"
	@echo  "    migrate Runs a database migration based on your local settings DB"
	@echo  "    redb	Rebuilds the dev DB"
	@echo  "    run 	Runs the devserver"

check: $(FLAKE8)
	- $(FLAKE8) $(PROJECT) --exclude migrations --max-line-length=80

$(FLAKE8):
	$(PIP) install flake8

tox: $(TOX)
	$(TOX) -e django19

$(TOX):
	$(PIP) install tox

coverage: $(COVERAGE)
	$(COVERAGE) run --source=$(PROJECT) manage.py test --settings=rssfeed.tests.settings.19
	$(COVERAGE) report
	$(COVERAGE) html

$(COVERAGE):
	$(PIP) install coverage

test:
	$(PYTHON) manage.py test --settings=rssfeed.tests.settings.19

$(VENV):
	virtualenv $(VENV)

ipython:
	$(PIP) install ipython

virtualenv: $(VENV)
	$(PIP) install -r rssfeed/tests/requirements/19.txt

clean-virtualenv:
	rm -rf $(VENV)