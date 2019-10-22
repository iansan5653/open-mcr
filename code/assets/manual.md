<!-- NOTE: This file is used to generate the manual.pdf, which must be
done as part of the build process (see /build_instructions.md) -->

# Bubble Sheet Reader: User Manual

## Printing and Scanning Bubble Sheets

### Printing Sheets

The bubble sheet form that must be used with this software is available as a PDF
file from the website. This form can be printed with any standard laser or
inkjet printer. For best results, print on white 8.5"x11" standard copier paper.
Colored sheets may still work, but they may be less reliable.

#### (Optional) Modifying the Bubble Sheet

If you would like to modify the bubble sheet to fit your need, the software will
support reading of a file with some edits. All of the text on the sheet except
the inner labels of the bubbles themselves can be safely modified. However, you
should not modify the location, size, or color of the bubbles or the corner
marks. The editable file is linked on the repository main page or you can modify
the PDF.

Examples of _acceptible_ changes include but are not limited to:

- Adding a logo, verification code, or additional instructions (but not near the
  corner marks or bubbles)
- Changing the "Test Form Code" label to something else
- Changing the font of the labels (but not the letters inside the bubbles)
- Removing the manual fill-in boxes
- Removing the signature and date
- Removing the light grey background stripes

#### Scanning Filled Sheets

Although the software is very flexible and most scanning methods should result
in acceptable results, the most fastest and most preferrable mode of scanning is
to use a printer with a document feed and scan the entire stack of exams using
the document feeder. Then use a break the resulting PDF file down into
individual images and place into a single directory.

When scanning answer keys, the order does not matter. They can be placed at the
beginning of the stack, the end, the middle, or shuffled throughout. All sheets
with a last name of `ZZZZZZZZZZZZ` will be treated as answer keys regardless of
position.

## (Optional) Creating Answer Keys

Creating answer keys is optional - if you don't want the software to score the
results for you, you can skip this section.

### Using the Bubble Sheets

If desired, you may create answer keys by simply filling out a bubble sheet and
making the last name `ZZZZZZZZZZZZ`. The first name, middle name, student ID,
and course ID will be ignored. The test form code should match the form code
that the students will use for that exam form. It can be a single letter (`A`,
`B`, `C`, `D`, `E`, or `F`) or any combination of those (ie, `[A|B]` [this
format of combining multiple is required]). This allows for up to
2<sup>6</sup>=64 possible different keys.

Intuitively, the correct answers should be provided using the questions on the
sheet. For each question, bubble in the correct answer. If the correct answer is
multiple letters, ie `A` _and_ `B`, then fill both in. Only fill as many answers
as there are questions. If students fill in answers beyond the number of
questions on their form code's key, the later answers will be ignored when
calculating their score.

### Using a CSV File

If you prefer not to enter the keys on paper, you can upload a CSV file with the
exam keys already made. This can be done by creating a spreadsheet in a program
like Excel and then saving as a "Comma-Separated Values (CSV)" file. The file
_must_ have the correct column names:

| Test Form Code | 1      | 2   | 3   | ... |
| -------------- | ------ | --- | --- | --- |
| A              | B      | D   | A   | ... |
| [A\|B]         | D      | C   | A   | ... |
| B              | [D\|E] | C   | D   | ... |
| ...            | ...    | ... | ... | ... |

_Note_: If a CSV file is provided, the software will still treat bubble sheets
with a last name of `ZZZZZZZZZZZZ` as answer keys, but the CSV file will take
precedence when keys conflict.

## Processing Scanned Sheets

In order to process scans with this program, they all need to be in the same
folder as PNG or JPG files. You can use Adobe Acrobat or another program to
split a PDF file into individual image files. There should be nothing else in
the folder. Subfolders will be ignored.

Here is an example of a possible file structure:

- scanned_sheets
  - image_1.png
  - image_2.png
  - image_3.png
  - image_4.jpg
  - image_5.jpg
  - subfolder
    - _Images here will be ignored._

To process the exam sheets, simple follow the instructions in the program. It
will guide you to select the input folder, optionally select the answer keys
file, and select an output folder.

### Converting Multiple Answers to `F`

In some instances (for example, if desire to process your exam results using
another software), you may want to treat all instances where students select
multiple answers in the same way. In this case, select the "Convert multiple
answers in a question to 'F'" option. Then, all questions for which the student
selected multiple answers will have the answer `F`. Since the answer choices on
the bubble sheet only range from `A` to `E`, this will make such instances
readily apparent.

## Overview of Output Files

_Note_: The selected output folder should be empty. If not, any existing CSV
files may be overwritten without warning.

If no answer keys were found, a single output CSV file will be saved in the
target folder. The file has columns for last name, first name, middle name, the
course ID, the student ID, and the form code, as well as one column for each
question.

Multiple answers are combined in a list form, separated by "|" characters. So if
a students selects A, B, and C, the answer is output as \[A|B|C\]. If they make
a mistake and select two letters in the same column for their name, it might be
output as "SM\[I|T\]H", which is an easy to see sign that an error was made.

### Scored Results

If answer keys were provided, then two additional files will be saved. One of
these is the answer keys, output in the same format as the student results
except without last name, first name, middle name, course ID, or student ID
columns. The other is the graded results. This will have the columns for last
name, first name, middle name, course ID, student ID, and form code, as well as
a total score percent (as a decimal number from `0` to `1`), a total score
quantity (as a sum of correct answers), and a column for each question. In this
file, the answers are simply output as `TRUE` or `FALSE` (`TRUE` indicating a
correct answer).
