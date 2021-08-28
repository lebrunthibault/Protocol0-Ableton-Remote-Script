from protocol0.enums.AbstractEnum import AbstractEnum


class ActionEnum(AbstractEnum):
    FOLD = "FOLD"  # fold set
    NEXT = "NEXT"  # repeat previous command
    SOLO = "SOLO"  # solo/unsolo track
    ARM = "ARM"  # arm/unarm track
    REC = "REC"   # record track
    UNDO = "UNDO"  # set undo
    DUPLICATE = "DUPLICATE"  # duplicate track
    LOOP = "LOOP"  # loop scene
    SHOW = "SHOW"   # show/hide instrument
