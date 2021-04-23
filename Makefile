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

check:
	make test
	make flake8
	make mypy