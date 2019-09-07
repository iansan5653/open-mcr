"""Tests for file-handling.py methods."""

import file_handling
from pathlib import Path


class TestListFilePaths:
  def test_examples(self):
    example_dir = Path(__file__).parent.parent / "examples"
    files = ["autar_a_a.png", "cochrane_j_l.png", "rico_a_b.png"]
    full_file_paths = [example_dir / file for file in files]
    assert file_handling.list_file_paths(example_dir) == full_file_paths


class TestFilterByExtensions:
  def test_single_extension(self):
    files = ["test.py", "test2.py", "test.txt", "test3.jpg"]
    extensions = [".py"]
    expected = ["test.py", "test2.py"]
    assert file_handling.filter_by_extensions(files, extensions) == expected

  def test_multiple_extensions(self):
    files = ["test.py", "test2.py", "test.txt", "test3.jpg"]
    extensions = [".py", ".jpg"]
    expected = ["test.py", "test2.py", "test3.jpg"]
    assert file_handling.filter_by_extensions(files, extensions) == expected

  def test_full_paths(self):
    files = [
        "c:/documents/example/test.py", "d:/sample/test2.py", "f:/test.txt",
        "c:/users/joe/test3.jpg"
    ]
    extensions = [".py", ".txt"]
    expected = [
        "c:/documents/example/test.py", "d:/sample/test2.py", "f:/test.txt"
    ]
    assert file_handling.filter_by_extensions(files, extensions) == expected