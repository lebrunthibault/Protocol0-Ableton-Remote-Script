.PHONY: test pretty flake8 mypy vulture check

test:
	cls
	pytest -s .

pretty:
	black .

flake8:
	cls
	flake8 .

mypy:
	cls
	mypy .

vulture:
	cls
	vulture . .\vulture_whitelist.py

check:
	make test
	make flake8
	make mypy
	make vulture