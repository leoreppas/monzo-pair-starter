.PHONY: venv install test

PY=python3
VENV?=.venv

venv:
	$(PY) -m venv $(VENV)
	. $(VENV)/bin/activate; pip install --upgrade pip

install: venv
	. $(VENV)/bin/activate; pip install -e .

test:
	. $(VENV)/bin/activate; pytest -q
