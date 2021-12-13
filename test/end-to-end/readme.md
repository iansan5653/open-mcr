# End-To-End Tests

The end-to-end tests run the CLI program against example datasets and compare the output CSV files
to expected output. Unlike unit tests, the end-to-end tests run the full program from start to
finish and test every part of execution.

## Test Setup

The `test_e2e.py` file runs end-to-end tests by locating all subdirectories in the `end_to_end`
directory. Each test is defined by a set of files in its subdirectory:

- `input/**` The input files including all images and keys.
- `output/**` The expected output files to compare against. When functionality changes, these files
  may need to be updated.
- `args.txt` Define additional arguments to pass to the CLI. For example, putting `--variant 150q`
  here will make the program run in 150-question mode. Leaving this file blank or not creating it
  will result in running with the default arguments (input and out paths plus `--disable-timestamp`).
  Any instance of `$$INPUT_DIR$$` in this file will be replaced with the full absolute input directory
  path.
