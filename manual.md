### Printing Bubble Sheets

The bubble sheet form that must be used with this software is available as a PDF
file [here](./bubble_sheet.pdf). This form can be printed with any standard
laser or inkjet printer. For best results, print on white 8.5"x11" standard
copier paper. Colored sheets may still work, but they may be less reliable.

#### Modifying the Bubble Sheet

If you would like to modify the bubble sheet to fit your need, the software will
support reading the file with some edits. All of the text on the sheet except
the inner labels of the bubbles themselves can be safely modified. However, you
should not modify the location, size, or color of the bubbles or the corner
marks. The editable file is [bubble_sheet.svg](./bubble_sheet.svg)

Examples of _acceptible_ changes include but are not limited to:

- Adding a logo, verification code, or additional instructions (but not near the
  corner marks or bubbles)
- Changing the "Test Form Code" label to something else
- Changing the font of the labels (but not the letters inside the bubbles)
- Removing the manual fill-in boxes
- Removing the signature and date
- Removing the light grey background stripes

### Creating Answer Keys

If desired, you may optionally create answer keys for use in scoring the exam
results. To do so, simply fill out a bubble sheet and make the last name
"ZZZZZZZZZZZZ". The first name, middle name, student ID, and course ID will be
ignored. The test form code should match the form code that the students will
use for that exam form. It can be a single letter (A, B, C, D, E, or F) or any
combination of those (ie, AB). THis allows for up to 2^6=64 possible different
forms.

Intuitively, the correct answers should be provided using the questions on the
sheet. For each question, bubble in the correct answer. If the correct answer is
multiple letters, ie A and B, then fill both in. Only fill as many answers as
there are questions. If students fill in answers beyond the number of questions
on their form code's key, the later answers will be ignored when calculating
their score.

### Scanning Filled Sheets

Although the software is very flexible and most scanning methods should result
in acceptable results, the most fastest and most preferrable mode of scanning is
to use a printer with a document feed and scan the entire stack of exams using
the document feeder. Then use a PDF software to break the resulting file down
into individual images and place into a single directory.

When scanning answer keys, the order does not matter. They can be placed at the
beginning of the stack, the end, the middle, or shuffled throughout. All sheets
with a last name of "ZZZZZZZZZZZZ" will be treated as answer keys regardless of
position.

### Processing Scans

In order to process scans with this program, they all need to be in the same
folder as PNG or JPG files. You can use Adobe Acrobat or another program to
split a PDF file into individual image files. There should be nothing else in
the folder.

Then simply run the program and select your folder in the selection box that
appears. After the program finishes, select an output folder for the data files
to be stored.

### Output Files

If no answer keys were found, a single output CSV file will be saved. The file
has columns for last name, first name, middle name, the course ID, the student
ID, and the form code, as well as one column for each question.

Multiple answers are combined in a list form, separated by "|" characters. So if
a students selects A, B, and C, the answer is output as \[A|B|C\]. If they make
a mistake and select two letters in the same column for their name, it might be
output as "SM\[I|T\]H", which is an easy to see sign that an error was made.

If answer keys were provided, then two additional files will be saved. One of
these is the answer keys, output in the same format as the student results
except without last name, first name, middle name, course ID, or student ID
columns. The other is the graded results. This will have the columns for last
name, first name, middle name, course ID, student ID, and form code, as well as
a total score percent (as a decimal number from 0 to 1) and a column for each
question. In this file, the answers are simply output as TRUE or FALSE (TRUE
indicating a correct answer).
