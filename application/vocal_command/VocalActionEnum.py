from protocol0.application.command.ClearLogsCommand import ClearLogsCommand
from protocol0.shared.AbstractEnum import AbstractEnum


class VocalActionEnum(AbstractEnum):
    """ NB: add previous commands """
    CLEAR = ClearLogsCommand
    # PLAY = "PLAY"  # play set
    # PAUSE = "PAUSE"  # pause set
    # STOP = "STOP"  # stop set
    # FOLD = "FOLD"  # fold set
    # NEXT = "NEXT"  # repeat previous command
    # SOLO = "SOLO"  # solo/unsolo track
    # ARM = "ARM"  # arm/unarm track
    # MONITOR = "MONITOR"  # change track monitoring
    # REC = "REC"  # record track
    # DUPLICATE = "DUPLICATE"  # duplicate track
    # LOOP = "LOOP"  # loop scene
    # SHOW = "SHOW"  # show/hide instrument
    # SPLIT = "SPLIT"  # split scene
