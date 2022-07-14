import inspect
from collections import namedtuple

from typing import Optional, Any

from protocol0.shared.Config import Config


def get_frame_info(frame_count=1):
    # type: (int) -> Optional[Any]
    call_frame = inspect.currentframe()
    for _ in range(frame_count):
        next_frame = call_frame.f_back
        if not next_frame:
            break
        call_frame = next_frame
    try:
        (filename, line, method_name, _, _) = inspect.getframeinfo(call_frame)
    except IndexError:
        return None
    filename = filename.replace(Config.PROJECT_ROOT + "\\", "").replace(
        Config.REMOTE_SCRIPTS_ROOT + "\\", ""
    )
    class_name = filename.replace(".py", "").split("\\")[-1]

    FrameInfo = namedtuple("FrameInfo", ["filename", "class_name", "line", "method_name"])
    return FrameInfo(filename=filename, class_name=class_name, line=line, method_name=method_name)
