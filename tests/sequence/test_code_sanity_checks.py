import os

from a_protocol_0.consts import PROTOCOL0_FOLDER


def test_sequence_is_always_returned():
    code_files = []
    for current_path, folders, files in os.walk(PROTOCOL0_FOLDER):
        if any([folder_name in current_path for folder_name in [".git", "tests", "pytest", "jupyter", ".ipynb_checkpoints", "scripts", "sequence"]]):
            continue
        for file in files:
            if file.endswith(".pyc") or file == "Protocol0.py":
                continue
            code_files.append(os.path.join(current_path, file))

    for code_file in code_files:
        with open(code_file, "r") as f:
            file_content = f.read()
            instantiated_sequences = file_content.count("Sequence(")
            returned_sequences = file_content.count("seq.done(")  # expecting coherent naming
            assert instantiated_sequences <= returned_sequences, code_file
