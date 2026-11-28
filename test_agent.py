import os
from agent import write_file, read_file, list_directory

def test_file_operations(tmp_path, monkeypatch):
    # Simulate typing 'y' if overwrite confirmation triggers
    monkeypatch.setattr("builtins.input", lambda _: "y")

    test_file = tmp_path / "sample.txt"
    res = write_file(str(test_file), "Hello CI/CD")
    assert "Success" in res
    assert read_file(str(test_file)) == "Hello CI/CD"

def test_list_directory():
    output = list_directory(".")
    assert "agent.py" in output