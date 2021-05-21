import sys

from utils import click_and_restore_pos, setup_logs, log

if __name__ == "__main__":
    setup_logs()
    x, y = int(sys.argv[1]), int(sys.argv[2])
    log("clicking at x: %s, y: %s" % (x, y))
    click_and_restore_pos(x, y)
