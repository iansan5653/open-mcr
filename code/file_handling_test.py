"""Tests for file-handling.py methods."""

import file_handling
from pathlib import Path, PurePath


class TestListFilePaths:
  def test_examples(self):
    example_dir = Path(__file__).parent.parent / "examples"
    files = ["autar_a_a.png", "cochrane_j_l.png", "rico_a_b.png"]
    full_file_paths = [example_dir / file for file in files]
    assert file_handling.list_file_paths(example_dir) == full_file_paths


class TestFilterByExtensions:
  def test_single_extension(self):
    file_names = ["test.py", "test2.py", "test.txt", "test3.jpg"]
    files = [PurePath(name) for name in file_names]
    extensions = [".py"]
    expected = [files[0], files[1]]
    assert file_handling.filter_by_extensions(files, extensions) == expected

  def test_multiple_extensions(self):
    file_names = ["test.py", "test2.py", "test.txt", "test3.jpg"]
    files = [PurePath(name) for name in file_names]
    extensions = [".py", ".jpg"]
    expected = [files[0], files[1], files[3]]
    assert file_handling.filter_by_extensions(files, extensions) == expected

  def test_full_paths(self):
    file_paths = [
        "c:/documents/example/test.py", "d:/sample/test2.py", "f:/test.txt",
        "c:/users/joe/test3.jpg"
    ]
    files = [PurePath(path) for path in file_paths]
    extensions = [".py", ".txt"]
    expected = [files[0], files[1], files[2]]
    assert file_handling.filter_by_extensions(files, extensions) == expected

  def test_combo_extension(self):
    file_names = ["test.py", "test2.tar.gz", "test.txt", "test3.jpg"]
    files = [PurePath(name) for name in file_names]
    extensions = [".tar.gz"]
    expected = [files[1]]
    assert file_handling.filter_by_extensions(files, extensions) == expected