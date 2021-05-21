import os

from typing import Generator, Any

from utils import setup_logs, log


class SerumPresetSynchronizer:
    PRESET_DIRECTORY = "C:\\Users\\thiba\\OneDrive\\Documents\\Xfer\\Serum Presets\\Presets"
    PROGRAM_CHANGE_FILENAME = "C:\\Users\\thiba\\OneDrive\\Documents\\Xfer\\Serum Presets\\System\\ProgramChanges.txt"

    @classmethod
    def get_preset_names(cls):
        # type: () -> Generator[str, Any, Any]
        for path, _, files in os.walk(cls.PRESET_DIRECTORY):
            relative_path = path.replace(cls.PRESET_DIRECTORY, "")
            if relative_path.startswith("\\_"):
                continue

            for name in files:
                if not name.endswith(".fxp"):
                    continue
                yield os.path.join(relative_path, name)

    @classmethod
    def synchronize(cls):
        # type: () -> None
        presets = list(cls.get_preset_names())
        with open(cls.PROGRAM_CHANGE_FILENAME, "w") as f:
            for preset in presets:
                f.write("%s\n" % preset)

        log("%d serum presets wrote to %s" % (len(presets), cls.PROGRAM_CHANGE_FILENAME))


if __name__ == "__main__":
    setup_logs()
    SerumPresetSynchronizer.synchronize()
