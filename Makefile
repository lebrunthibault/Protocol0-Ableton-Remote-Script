test:
	cls
	pytest -s .

pretty:
	black .

lint:
	cls
	flake8 .
	mypy .

check:
	make test
	make lint