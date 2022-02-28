import sys

from protocol0.tests.fixtures.p0 import monkey_patch_static
from protocol0.tests.infra.scheduler.TickSchedulerTest import TickSchedulerTest

sys.dont_write_bytecode = True  # noqa

monkey_patch_static()
