.PHONY: test flake8 mypy vulture pycharm check

test:
	cls
	.\venv\Scripts\pytest -s .

flake8:
	cls
	.\venv\Scripts\flake8 .

mypy:
	cls
	mypy .

vulture:
	cls
	.\venv\Scripts\vulture . .\vulture_whitelist.py --exclude=venv/

#pycharm:
#	# not working
#	pycharm64.exe inspect .. .\InspectionProfile.xml .\InspectionResults -d .

check:
	make test
	make flake8
	make mypy
