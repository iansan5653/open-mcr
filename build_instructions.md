# Build Instructions

The following instructions show how to build the program into a single `.exe`
file that can be run to install the software.

1. Install the required modules from [`requirements.txt`](requirements.txt) if
   you haven't already.
2. Open a terminal in the root directory.
3. Run the build command:
   ```sh
   pyinstaller -p code -y -w --icon=code/icon.ico code/bubble_sheet_reader.py
   ```
4. Use a markdown to PDF converter to generate a `manual.pdf` file and place it
   in `./dist/bubble_sheet_reader`.
5. Install NSIS if you haven't already.
6. Run NSIS and compile [`installer.nsi`](installer.nsi).
