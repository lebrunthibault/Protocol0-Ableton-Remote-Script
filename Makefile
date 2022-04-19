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
	.\venv\Scripts\vulture . .\vulture_whitelist.py --make-whitelist --exclude=venv/,command/,command_handler/,InputRoutingTypeEnum.py,InputRoutingChannelEnum.py,OutputRoutingTypeEnum.py,Push2MainModeEnum.py,Push2MatrixModeEnum.py,BarLengthEnum.py,Push2Service.py --ignore-names=Optional,Tuple,Deque,Union,CollectionsSequence,Iterator,TracebackType,Func,decorate,to_json,device_on

#pycharm:
#	# not working
#	pycharm64.exe inspect .. .\InspectionProfile.xml .\InspectionResults -d .

check:
	make flake8
	make mypy
	make vulture
	make test
