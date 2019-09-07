"""Functions and utilities related to importing and exporting files."""

import typing
import os


def list_file_paths(directory: str) -> typing.List[str]:
  """Returns a list of full paths to all the files that are direct children.

  Does not include directories or files in subdirectories.

  Params:
    directory: The full path to the directory to look for files in.

  Returns:
    List of full paths to the files found.
  """
  all_items = os.listdir(directory)
  full_paths = [os.path.join(directory, name) for name in all_items]
  only_files = [
      name for (full_path, name) in zip(full_paths, all_items)
      if os.path.isfile(full_path)
  ]
  return only_files


def filter_by_extensions(files: typing.List[str],
                         extensions: typing.List[str]) -> typing.List[str]:
  """Returns a list of full paths to all the files that have the extensions
  given.

  Does not include files in subdirectories.

  Params:
    files: A list of all the files in the directory.
    extensions: List of file extensions, with leading dots (ie, `[".txt"]`).
  
  Returns:
    List of full paths to the files found.
  """
  return [path for path in files if os.path.splitext(path)[1] in extensions]
