.PHONY: venv install test lint format


PY=python3
VENV?=.venv


venv:
$(PY) -m venv $(VENV)
. $(VENV)/bin/activate; pip install --upgrade pip


install: venv
. $(VENV)/bin/activate; pip install -e .


format:
. $(VENV)/bin/activate; python -m pip install black ruff >/dev/null 2>&1 || true
. $(VENV)/bin/activate; black src tests
. $(VENV)/bin/activate; ruff check --fix src tests || true


test:
. $(VENV)/bin/activate; pytest -q


# quick alias you can map to a hotkey
T?=
ktest:
. $(VENV)/bin/activate; pytest -q -k "$(T)"