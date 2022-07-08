.PHONY: test flake8 mypy vulture pycharm check

test:
	clear
	.\venv\Scripts\pytest -s .

flake8:
	clear
	.\venv\Scripts\flake8 .

mypy:
	clear
	mypy .

vulture:
	clear
	.\venv\Scripts\vulture . .\vulture_whitelist.py --make-whitelist --exclude=venv/,command/,command_handler/,push2/,InputRoutingTypeEnum.py,InputRoutingChannelEnum.py,OutputRoutingTypeEnum.py,BarLengthEnum.py --ignore-names=Optional,Tuple,Deque,Union,CollectionsSequence,Iterator,TracebackType,Func,decorate,subject,TRACK_COLOR

#pycharm:
#	# not working
#	pycharm64.exe inspect .. .\InspectionProfile.xml .\InspectionResults -d .

check:
	make flake8
	make mypy
	make vulture
	make test
