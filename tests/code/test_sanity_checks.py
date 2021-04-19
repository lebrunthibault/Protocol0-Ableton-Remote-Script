import os
from collections import Iterator

import pytest
from typing import List

from a_protocol_0.consts import ROOT_DIR
from a_protocol_0.tests.windows import focus_pycharm


def get_code_filenames(exclude_folder_list=[]):
    # type: (List[str]) -> Iterator[str]
    for current_path, folders, files in os.walk(ROOT_DIR):
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


@pytest.mark.skip(reason="slow")
def test_sequence_pattern():
    # type: () -> None
    """ test sequence pattern is respected """
    for filename in get_code_filenames(["sequence", "tests"]):
        with open(filename, "r") as f:
            file_content = f.read()
            instantiated_sequences = file_content.count(" Sequence(")
            returned_sequences = file_content.count("seq.done(")  # expecting coherent naming
            assert instantiated_sequences <= returned_sequences, "invalid sequence code in %s" % filename.replace(
                ROOT_DIR, ""
            )


@pytest.mark.skip(reason="slow")
def test_all_methods_typed():
    # type: () -> None
    """ used when refactoring untyped code """
    for filename in get_code_filenames():
        with open(filename, "r") as f:
            base_filename = filename.replace(ROOT_DIR, "")
            lines = f.readlines()
            for index, line in enumerate(lines):
                if "def " in line and "):" in line:
                    if "type: " not in lines[index + 1]:
                        os.system("pycharm64.exe --line %d ./%s" % (index + 1, base_filename))
                        focus_pycharm()
                        assert False, "untyped function in %s:%d\n%s" % (
                            filename,
                            index + 1,
                            line,
                        )
