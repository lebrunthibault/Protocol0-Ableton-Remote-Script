import os

import pytest
from typing import List, Optional, Iterator

from protocol0.shared.Config import Config


def get_code_filenames(exclude_folder_list=None):
    # type: (Optional[List[str]]) -> Iterator[str]
    exclude_folder_list = (exclude_folder_list or []) + [
        ".git",
        "pytest",
        "jupyter",
        ".ipynb_checkpoints",
        "venv",
    ]
    for current_path, _, files in os.walk(Config.PROJECT_ROOT):
        if any(folder_name in current_path for folder_name in exclude_folder_list):
            continue
        for filename in files:
            if filename.endswith(".pyc") or filename in ("Protocol0.py", "__init__.py"):
                continue
            yield os.path.join(current_path, filename)


@pytest.mark.skip(reason="slow")
def test_sequence_pattern():
    # type: () -> None
    """test sequence pattern is respected"""
    for filename in get_code_filenames(["sequence", "tests"]):
        with open(filename, "r") as f:
            file_content = f.read()
            instantiated_sequences_count = file_content.count(" Sequence(")
            returned_sequences_count = file_content.count("seq.done(")  # expecting coherent naming
            assert (
                instantiated_sequences_count <= returned_sequences_count
            ), "invalid sequence lint in %s" % filename.replace(Config.PROJECT_ROOT, "")
