import os
from collections import Iterator

import pytest
from typing import List, Optional

from protocol0.application.constants import PROJECT_ROOT


@pytest.mark.skip(reason="slow")
def get_code_filenames(exclude_folder_list=None):
    # type: (Optional[List[str]]) -> Iterator[str]
    exclude_folder_list = (exclude_folder_list or []) + [
        ".git",
        "pytest",
        "jupyter",
        ".ipynb_checkpoints",
        "venv"
    ]
    for current_path, _, files in os.walk(PROJECT_ROOT):
        if any(
                folder_name in current_path
                for folder_name in exclude_folder_list
        ):
            continue
        for filename in files:
            if filename.endswith(".pyc") or filename in ("Protocol0.py", "__init__.py", "callback_descriptor.py"):
                continue
            yield os.path.join(current_path, filename)


@pytest.mark.skip(reason="slow")
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
