.PHONY: test black flake8 mypy vulture pycharm check

test:
	cls
	pytest -s .

black:
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

#pycharm:
#	# not working
#	pycharm64.exe inspect .. .\InspectionProfile.xml .\InspectionResults -d .

check:
	make test
	make flake8
	make mypy
	make vulture