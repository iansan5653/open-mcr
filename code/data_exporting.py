""""""
import csv
import pathlib
import typing

from grid_info import NUM_QUESTIONS, Field, RealOrVirtualField, VirtualField
import list_utils

# If you change these, also update the manual!
COLUMN_NAMES: typing.Dict[RealOrVirtualField, str] = {
    Field.LAST_NAME: "Last Name",
    Field.FIRST_NAME: "First Name",
    Field.MIDDLE_NAME: "Middle Name",
    Field.STUDENT_ID: "Student ID",
    Field.COURSE_ID: "Course ID",
    Field.TEST_FORM_CODE: "Test Form Code",
    VirtualField.SCORE: "Total Score (%)",
    VirtualField.POINTS: "Total Points"
}

KEY_NOT_FOUND_MESSAGE = "NO KEY FOUND"


class OutputSheet():
    """A lightweight matrix of data to be exported. Faster than a dataframe but
    can be easily converted to one when the need arises."""
    # Must be structured as: field_a, field_b, ..., 1, 2, 3, ...
    data: typing.List[typing.List[str]]
    field_columns: typing.List[RealOrVirtualField]
    num_questions: int = NUM_QUESTIONS
    row_count: int
    first_question_column_index: int

    def __init__(self, columns: typing.List[RealOrVirtualField]):
        self.field_columns = columns
        field_column_names = [COLUMN_NAMES[column] for column in columns]
        answer_columns = [str(i + 1) for i in range(self.num_questions)]
        self.first_question_column_index = len(field_column_names)
        self.data = [field_column_names + answer_columns]
        self.row_count = 0

    def save(self, path: pathlib.PurePath):
        with open(str(path), 'w+', newline='') as output_file:
            writer = csv.writer(output_file)
            writer.writerows(self.data)

    def add(self, fields: typing.Dict[RealOrVirtualField, str],
            answers: typing.List[str]):
        row: typing.List[str] = []
        for column in self.field_columns:
            try:
                row.append(fields[column])
            except KeyError:
                row.append('')
        self.data.append(row + answers)
        self.row_count = len(self.data) - 1

    def add_file(self, csvfile: pathlib.Path):
        with open(str(csvfile), 'r', newline='') as file:
            reader = csv.reader(file)
            names = next(reader)
            # The fields that correspond with the columns
            keys: typing.List[typing.Union[RealOrVirtualField, None]] = []
            for name in names:
                try:
                    key = next(key for key, value in COLUMN_NAMES.items()
                               if value == name)
                except StopIteration:
                    key = None
                keys.append(key)
            for row in reader:
                fields = {
                    key: value
                    for key, value in list(zip(keys, row))
                    [:self.first_question_column_index] if key is not None
                }
                answers = row[self.first_question_column_index:]
                self.add(fields, answers)

    def clean_up(self, replace_empty_with: str = ""):
        """Removes the extra headings from the heading row and replaces blank
        cells with `replace_empty_with`. Pads any short rows with that value to
        make all rows the same length. """
        # Finds the length of the longest row by subtracting the smallest index
        # of the first element in a row that is not blank from the length of the
        # header row.
        longest_length = len(self.data[0]) - min([
            next(i for i, ans in enumerate(reversed(row)) if ans != "")
            for row in self.data[1:]
        ])
        for i, row in enumerate(self.data):
            cleaned_row = row[:self.first_question_column_index] + [
                item if (item != "") else replace_empty_with
                for item in row[self.first_question_column_index:]
            ]
            difference = longest_length - len(cleaned_row)
            if (difference < 0):
                cleaned_row = cleaned_row[:longest_length]
            elif (difference > 0):
                cleaned_row += [replace_empty_with] * difference
            self.data[i] = cleaned_row


def save_reordered_version(sheet: OutputSheet, arrangement_file: pathlib.Path,
                           save_path: pathlib.Path):
    """Reorder the output sheet based on a key arrangement file and save CSV."""
    # order_map will be a dict matching form code keys to a list where the
    # new index of question `i` in `key` is `order_map[key][i]`
    order_map: typing.Dict[str, typing.List[int]] = {}
    with open(str(arrangement_file), 'r', newline='') as file:
        reader = csv.reader(file)
        names = next(reader)
        form_code_index = list_utils.find_index(
            names, COLUMN_NAMES[Field.TEST_FORM_CODE])
        first_answer_index = list_utils.find_index(names, "1")
        for form in reader:
            form_code = form[form_code_index]
            to_order_zero_ind = [int(n) - 1 for n in form[first_answer_index:]]
            order_map[form_code] = to_order_zero_ind
    sheet_form_code_index = list_utils.find_index(
        sheet.data[0], COLUMN_NAMES[Field.TEST_FORM_CODE])
    sheet_first_answer_index = list_utils.find_index(sheet.data[0], "1")
    sheet_total_score_index = list_utils.find_index(
        sheet.data[0], COLUMN_NAMES[VirtualField.SCORE])
    results = [sheet.data[0]]
    for row in sheet.data[1:]:
        form_code = row[sheet_form_code_index]
        if row[sheet_total_score_index] != KEY_NOT_FOUND_MESSAGE:
            try:
                order_map[form_code]
            except IndexError:
                results.append(row)
            else:
                row_reordered = row[:sheet_first_answer_index] + [
                    row[ind + sheet_first_answer_index]
                    for ind in order_map[form_code]
                ]
                results.append(row_reordered)
        else:
            results.append(row)
    with open(str(save_path), 'w+', newline='') as output_file:
        writer = csv.writer(output_file)
        writer.writerows(results)
