import sys

from typing import Optional
from utils.log import setup_logs
from utils.window import focus_window, SearchType

if __name__ == "__main__":
    setup_logs()
    try:
        search_type = sys.argv[2]  # type: Optional[str]
    except IndexError:
        search_type = None

    search_type = SearchType.get_from_value(search_type, SearchType.NAME)  # type: SearchType

    focus_window(sys.argv[1], search_type)
