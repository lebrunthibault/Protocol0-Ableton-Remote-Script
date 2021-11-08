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
	.\venv\Scripts\vulture . .\vulture_whitelist.py --exclude=venv/,BarLengthEnum.py,TrackSearchKeywordEnum.py --ignore-names=Optional,Generator,Func,Tuple,Deque,Union,CollectionsSequence,NoReturn,Iterator,TracebackType,StringOrNumber,decorate

#pycharm:
#	# not working
#	pycharm64.exe inspect .. .\InspectionProfile.xml .\InspectionResults -d .

check:
	make flake8
	make mypy
	make vulture
	make test
