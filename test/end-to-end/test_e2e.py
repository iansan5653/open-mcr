import subprocess
from pathlib import Path
import sys
import pytest

current_dir = Path(__file__).parent
open_mcr_path = current_dir.parent.parent / "code" / "main.py"

@pytest.mark.parametrize("path", [path for path in current_dir.iterdir() if path.is_dir() and path.name != "__pycache__"])
def test_e2e(path: Path):
    input_path = str(path / "input")
    additional_args_path = path / "args.txt"
    additional_raw_args = additional_args_path.read_text().split() if additional_args_path.exists() else []
    additional_args = [arg.replace("$$INPUT_DIR$$", f"{input_path}/") for arg in additional_raw_args]

    actual_output_path = path / "output"
    actual_output_path.mkdir(exist_ok=True)

    subprocess.check_call([
      sys.executable or 'python',
      str(open_mcr_path),
      input_path,
      str(actual_output_path),
      "--disable-timestamp",
      "--sort"
    ] + additional_args)

    expected_output_path = path / "output"

    for actual_output_file in actual_output_path.iterdir():
        actual_output = actual_output_file.read_text()
        expected_output_file = expected_output_path / actual_output_file.name
        expected_output = expected_output_file.read_text()
        assert actual_output == expected_output
