## ![OpenMCR](src/assets/wordmark.png)

### _Free and Open-Source Multiple Choice Exam Reader_

[![Continuous Integration](https://github.com/iansan5653/open-mcr/actions/workflows/continuous_integration.yml/badge.svg)](https://github.com/iansan5653/open-mcr/actions/workflows/continuous_integration.yml)

> **Warning**
> As per the license of this software, no warranty is implied. The software is
> stable but there still may be bugs. Given that students' grades are at stake,
> please be sure to audit the results - particularly when working with low-quality scans.

## Background

Commercially available OMR (optical mark recognition) exam sheets, scanners, and
processing software can cost educators and educational institutions thousands of
dollars per year. In response to this, OpenMCR has been developed as a free and
easy-to-use alternative. The tool includes a multiple choice exam sheet and
works with any scanner and printer.

This software and the
corresponding multiple choice sheet were developed as an independent study
project by Ian Sanders, a mechanical engineering student at the University of
South Florida, under the direction of Dr. Autar Kaw.

For a detailed discussion of the algorithm and features in use, please
[read the report](https://github.com/iansan5653/open-mcr-report/releases/tag/1.0.0)
as submitted for the original independent study course.

## Installation Instructions

Currently, packaged executables are only provided for Windows. For other operating
systems, see [Running From Source](#running-from-source--cli).

### Windows Installation

To install the utility, simply download the latest `.exe` file from from the
[releases](https://github.com/iansan5653/open-mcr/releases) page and
install it. After installation, check your Start menu for a shortcut.

### Running Without Install

For users who cannot or do not want to install the software on their machine,
ZIP file packages are also available for each [release](https://github.com/iansan5653/open-mcr/releases). Download the file,
extract it anywhere on your machine, and run the `main.exe` file. This method
does not require administrator priveleges.

### Running From Source / CLI

If you wish to customize the software, use the command line interface, or run it
on a non-Windows device, you can run the Python program directly from the source files. This
requires Python and Pip to be installed on your machine.

1. Clone the reposotory using Git, or download and extract the latest `Source code (zip)` file from
  [releases](https://github.com/iansan5653/open-mcr/releases).
2. Open a terminal / command prompt in the extracted directory.
3. On Mac machines with fresh Python installations, you will to update TKinter from the default.
4. Run `pip3 install -r requirements.txt` to install dependencies.
7. Run `python3 src/main.py` for the CLI interface or `python3 src/main_gui.py` for the graphical interface.

> **Note**: On MacOS, if you see a black screen when running the GUI, you need to uninstall Python, install TKinter, and
> then reinstall Python. The easiest way to do this is to manage your installation with Homebrew as described [here](https://apple.stackexchange.com/a/315121).

> **Note**: On Linux machines, you may see an error message that `opencv` or `tkinter` are not found.
> If you see this, install those dependencies by running `sudo apt-get install python3-opencv python3-tk` and then try again.

### Codespaces

For development, a pre-made environment is available in [Codespaces](https://github.com/features/codespaces):

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/iansan5653/open-mcr?quickstart=1)

> [!NOTE]
> The configuration auomatically installs the [`desktop-lite`](https://github.com/devcontainers/features/tree/main/src/desktop-lite)
> feature for running the GUI. This environment can be accessed in your browser through the forwarded `6080` port. The
> desktop password is `vscode`.

## Printable Multiple Choice Sheet

The multiple choice sheet that must be used with this software is available
for printing here:

* [75 Question Variant](https://github.com/iansan5653/open-mcr/raw/master/src/assets/multiple_choice_sheet_75q.pdf)
* [150 Question Variant](https://github.com/iansan5653/open-mcr/raw/master/src/assets/multiple_choice_sheet_150q.pdf)

## Usage Instructions

Run the program by finding it in your Start menu after installing.

For full operating instructions, see the [Manual](src/assets/manual.md) or
click the <kbd>Open Help</kbd> button in the software.

## Feedback / Bug Reports

To report a bug, request a new feature, or provide feedback, please
[file an issue](https://github.com/iansan5653/open-mcr/issues/new).

## License

### Software License

Copyright (C) 2019 Ian Sanders

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

For the full license text, see [license.txt](./license.txt).

### Multiple Choice Sheet License

The multiple choice sheet distributed with this software is licensed under the
Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International license
(CC BY-NC-SA 4.0). In summary, this means that you are free to distribute and
modify the document so long as you share it under the same license, provide
attribution, and do not use it for commercial purposes. For the full license,
see
[the Creative Commons website](https://creativecommons.org/licenses/by-nc-sa/4.0/).

**Note**: You are explicitly _allowed_ to distribute the multiple choice sheet
without attribution if using it unmodified for educational purpose and not
in any way implying that it is your own work. This is an exception to the
Creative Commons terms. 
