import os
from collections import Iterator

import pytest
from typing import List

from protocol0.config import PROJECT_ROOT


def get_code_filenames(exclude_folder_list=[]):
    # type: (List[str]) -> Iterator[str]
    for current_path, _, files in os.walk(PROJECT_ROOT):
        if any(
                folder_name in current_path
                for folder_name in [
                                       ".git",
                                       "pytest",
                                       "jupyter",
                                       ".ipynb_checkpoints",
                                   ]
                                   + exclude_folder_list
        ):
            continue
        for file in files:
            if file.endswith(".pyc") or file in ("Protocol0.py", "__init__.py", "callback_descriptor.py"):
                continue
            yield os.path.join(current_path, file)


# @pytest.mark.skip(reason="slow")
def test_sequence_pattern():
    # type: () -> None
    """ test sequence pattern is respected """
    for filename in get_code_filenames(["sequence", "tests"]):
        with open(filename, "r") as f:
            file_content = f.read()
            instantiated_sequences_count = file_content.count(" Sequence(")
            returned_sequences_count = file_content.count("seq.done(")  # expecting coherent naming
            assert (
                    instantiated_sequences_count <= returned_sequences_count
            ), "invalid sequence code in %s" % filename.replace(PROJECT_ROOT, "")


@pytest.mark.skip(reason="slow")
def test_all_methods_typed():
    # type: () -> None
    """ used when refactoring untyped code """
    for filename in get_code_filenames():
        with open(filename, "r") as f:
            base_filename = filename.replace(PROJECT_ROOT, "")
            lines = f.readlines()
            for index, line in enumerate(lines):
                if "def " in line and "):" in line:
                    if "type: " not in lines[index + 1]:
                        os.system("pycharm64.exe --line %d ./%s" % (index + 1, base_filename))
                        assert False, "untyped function in %s:%d\n%s" % (
                            filename,
                            index + 1,
                            line,
                        )
