.PHONY: setup run test

setup:
	python3 -m venv .venv
	.venv/bin/pip install -r requirements.txt

run:
	.venv/bin/python backend/server.py

test:
	.venv/bin/python -m unittest discover -s tests -v