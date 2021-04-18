test:
	cls
	pytest -s .

lint:
	cls
	flake8 .
	mypy .