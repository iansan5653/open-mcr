## ![OpenMCR](code/assets/wordmark.png)

### _Free and Open-Source Multiple Choice Exam Reader_

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

## Installation Instructions

Currently, installers are only provided for Windows. For other operating
systems, see [Running From Source](#running-from-source).

### Windows Installation

To install the utility, simply download the latest `.exe` file from from the
[releases](https://github.com/iansan5653/open-mcr/releases) page and
install it. After installation, check your Start menu for a shortcut.

### Running Without Install

For users who cannot or do not want to install the software on their machine,
ZIP file packages are also available for each [release](https://github.com/iansan5653/open-mcr/releases). Download the file,
extract it anywhere on your machine, and run the `main.exe` file. This method
does not require administrator priveleges.

### Running From Source

If you wish to customize the software or you need to run it on a non-Windows
device, you can run the Python program directly from the source files. This
requires Python to be installed on your machine. Download
the latest `Source code (zip)` file from [releases](https://github.com/iansan5653/open-mcr/releases).
Extract the file and open a terminal / command prompt in the extracted directory.
Run the command `python code/main.py`.

_Note_: This software has not been tested on other operating systems and support
is not guarunteed. If you find a bug, please file an [issue](https://github.com/iansan5653/open-mcr/issues).

## Printable Multiple Choice Sheet

The multiple choice sheet that must be used with this software is available
for printing here:

* [75 Question Variant](https://github.com/iansan5653/open-mcr/raw/master/code/assets/multiple_choice_sheet_75q.pdf)
* [100 Question Variant](https://github.com/iansan5653/open-mcr/raw/master/code/assets/multiple_choice_sheet_100q.pdf)

## Usage Instructions

Run the program by finding it in your Start menu after installing.

For full operating instructions, see the [Manual](code/assets/manual.md) or
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