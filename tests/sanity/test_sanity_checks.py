import os

from a_protocol_0.consts import ROOT_DIR


def get_code_filenames():
    for current_path, folders, files in os.walk(ROOT_DIR):
        if any(
            folder_name in current_path
            for folder_name in [
                ".git",
                "tests",
                "pytest",
                "jupyter",
                ".ipynb_checkpoints",
                "scripts",
                "sequence",
            ]
        ):
            continue
        for file in files:
            if file.endswith(".pyc") or file in ("Protocol0.py", "__init__.py", "callback_descriptor.py"):
                continue
            yield os.path.join(current_path, file)


def test_sequence_pattern():
    """ test sequence pattern is respected """
    for filename in get_code_filenames():
        with open(filename, "r") as f:
            file_content = f.read()
            instantiated_sequences = file_content.count(" Sequence(")
            returned_sequences = file_content.count("seq.done(")  # expecting coherent naming
            assert instantiated_sequences <= returned_sequences, "invalid sequence code in %s" % filename.replace(
                ROOT_DIR, ""
            )


def test_init_has_arguments():
    """ rudimentary code sanity checks """
    for filename in get_code_filenames():
        with open(filename, "r") as f:
            file_content = f.read()
            base_filename = filename.replace(ROOT_DIR, "")
            assert file_content.count("def __init__") <= file_content.count("super("), (
                "super not called in %s" % base_filename
            )
            assert file_content.find("__init__()") == -1, "__init__ called without args in %s" % base_filename
