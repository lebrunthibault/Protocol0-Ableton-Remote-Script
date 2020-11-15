import sys

sys.path.insert(0, "C:\Python27\Lib\site-packages")
sys.path.insert(0, "C:\Python27")
sys.path.insert(0, "C:\Python27\Lib")

from .Protocol0 import Protocol0


def create_instance(c_instance):
    return Protocol0(c_instance)
