test:
	cls
	pytest -s .

pretty:
	black .

lint:
	cls
	flake8 .
	mypy .