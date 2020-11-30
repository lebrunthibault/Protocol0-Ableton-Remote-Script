import sys

sys.path.insert(0, "C:\Python27\Lib\site-packages")
sys.path.insert(0, "C:\Python27")
sys.path.insert(0, "C:\Python27\Lib")

from .Protocol0Component import Protocol0Component
from .Protocol0 import Protocol0


def create_instance(*a):
    ins = Protocol0(*a)
    with ins.component_guard():
        ins.protocol0_component = Protocol0Component(control_surface=ins)
    return ins
