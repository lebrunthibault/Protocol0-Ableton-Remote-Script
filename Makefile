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
	.\venv\Scripts\vulture . .\vulture_whitelist.py --make-whitelist --exclude=venv/,InputRoutingTypeEnum.py,InputRoutingChannelEnum.py,OutputRoutingTypeEnum.py,Push2InstrumentModeEnum.py,Push2MainModeEnum.py,Push2MatrixModeEnum.py,CurrentMonitoringStateEnum.py,BarLengthEnum.py,TrackSearchKeywordEnum.py,ApiRoutesManager.py,LOMAnalyzer.py,Push2Manager.py --ignore-names=Any,Optional,Generator,Tuple,Deque,Union,CollectionsSequence,NoReturn,Iterator,TracebackType,StringOrNumber,Func,decorate,midi_server_check_timeout_scheduler_event,vocalCommandManager,api_exposable_class,_on_selected,*push2*,to_json,device_on,EXTERNAL_INSTRUMENT_DEVICE_HARDWARE_LATENCY

#pycharm:
#	# not working
#	pycharm64.exe inspect .. .\InspectionProfile.xml .\InspectionResults -d .

check:
	make flake8
	make mypy
	make vulture
	make test
