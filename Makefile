.PHONY: install run lint format

install:
	pip install -r requirements.txt

run:
	python -m bot.main

lint:
	python -m compileall .
