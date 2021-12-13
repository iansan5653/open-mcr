""""""
import csv
import operator
import os
import pathlib
import typing as tp
from datetime import datetime

import list_utils
from grid_info import Field, RealOrVirtualField, VirtualField

# If you change these, also update the manual!
COLUMN_NAMES: tp.Dict[RealOrVirtualField, str] = {
    Field.LAST_NAME: "Last Name",
    Field.FIRST_NAME: "First Name",
    Field.MIDDLE_NAME: "Middle Name",
    Field.TEST_FORM_CODE: "Test Form Code",
    Field.STUDENT_ID: "Student ID",
    Field.COURSE_ID: "Course ID",
    Field.IMAGE_FILE: 'Source File',
    VirtualField.SCORE: "Total Score (%)",
    VirtualField.POINTS: "Total Points"
}

KEY_NOT_FOUND_MESSAGE = "NO KEY FOUND"


def format_timestamp_for_file(timestamp: tp.Optional[datetime]) -> str:
    return timestamp.isoformat(sep="_").replace(":", "-") + "__" if timestamp else ""


def make_dir_if_not_exists(path: pathlib.Path):
    if not os.path.exists(str(path)):
        os.makedirs(str(path))


def validate_order_map(order_map: tp.Dict[str, tp.List[int]],
                       num_questions: int):
    """Validate the given order map and throw ValueError if the map is invalid."""
    for [form_code, map_list] in order_map.items():
        if (min(map_list) != 1 or max(map_list) != num_questions
                or len(set(map_list)) != num_questions):
            raise ValueError(
                f"Arrangement file entry for '{form_code}' is invalid. All arrangement file entries must contain one of each index from 1 to the number of questions."
            )

def save_csv(data: tp.List[tp.List[str]], path: pathlib.PurePath):
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(data)

class OutputSheet():
    """A lightweight matrix of data to be exported. Faster than a dataframe but
    can be easily converted to one when the need arises."""
    # Must be structured as: field_a, field_b, ..., Q1, Q2, Q3, ...
    data: tp.List[tp.List[str]]
    field_columns: tp.List[RealOrVirtualField]
    num_questions: int
    row_count: int
    first_question_column_index: int
    form_code_column_index: tp.Optional[int]

    def __init__(self, columns: tp.List[RealOrVirtualField], num_questions: int):
        self.field_columns = columns
        self.num_questions = num_questions
        field_column_names = [COLUMN_NAMES[column] for column in columns]
        answer_columns = [f"Q{i + 1}" for i in range(self.num_questions)]
        self.first_question_column_index = len(field_column_names)
        self.form_code_column_index = self.field_columns.index(
            Field.TEST_FORM_CODE) if (Field.TEST_FORM_CODE in self.field_columns) else None
        self.data = [field_column_names + answer_columns]
        self.row_count = 0

    def save(self, path: pathlib.PurePath, filebasename: str, sort: bool,
             timestamp: tp.Optional[datetime], transpose: bool = False) -> pathlib.PurePath:
        if sort:
            self.sortByName()
        output_path = path / f"{format_timestamp_for_file(timestamp)}{filebasename}.csv"
        data = self.data
        if(transpose):
            data = list_utils.transpose(data)
        save_csv(data, output_path)
        return output_path

    def delete_field_column(self, column: RealOrVirtualField):
        deleted_column_index = self.field_columns.index(column)
        self.field_columns.pop(deleted_column_index)
        self.data = [
            list_utils.remove_index(row, deleted_column_index)
            for row in self.data
        ]

    def sortByName(self):
        data = self.data[1:]
        col_names = self.data[0]
        try:
            primary_index = list_utils.find_index(
                col_names, COLUMN_NAMES[Field.LAST_NAME])
            secondary_index = list_utils.find_index(
                col_names, COLUMN_NAMES[Field.FIRST_NAME])
            tertiary_index = list_utils.find_index(
                col_names, COLUMN_NAMES[Field.MIDDLE_NAME])
        except StopIteration:
            try:
                primary_index = list_utils.find_index(
                    col_names, COLUMN_NAMES[Field.TEST_FORM_CODE])
                secondary_index = None
                tertiary_index = None
            except StopIteration:
                return
        if tertiary_index is not None:
            data = sorted(data, key=operator.itemgetter(tertiary_index))
        if secondary_index is not None:
            data = sorted(data, key=operator.itemgetter(secondary_index))
        data = sorted(data, key=operator.itemgetter(primary_index))
        self.data = [col_names] + data

    def add(self, fields: tp.Dict[RealOrVirtualField, str],
            answers: tp.List[str]):
        row: tp.List[str] = []
        for column in self.field_columns:
            try:
                row.append(fields[column].strip())
            except KeyError:
                row.append('')
        self.data.append(row + list_utils.strip_all(answers))
        self.row_count = len(self.data) - 1

    def add_file(self, csvfile: pathlib.Path):
        with open(str(csvfile), 'r', newline='') as file:
            reader = csv.reader(file)
            names = next(reader)
            # The fields that correspond with the columns
            keys: tp.List[tp.Union[RealOrVirtualField, None]] = []
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
        # Finds the length of the longest row by subtracting the minimum number of trailing empty elements
        longest_length = len(self.data[0]) - min([
            list_utils.count_trailing_empty_elements(row)
            for row in self.data[1:]
        ])
        self.data[0] = self.data[0][:longest_length]
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

    def reorder(self, arrangement_file: pathlib.Path):
        """Reorder the sheet based on an arrangement map file.

        Raises TypeError if invalid arrangement file.

        Results will have empty form code index."""
        # TODO: Validate arrangement file.
        # order_map will be a dict matching form code keys to a list where the
        # new index of question `i` in `key` is `order_map[key][i]`
        order_map: tp.Dict[str, tp.List[int]] = {}
        validate_order_map(order_map, self.num_questions)

        with open(str(arrangement_file), 'r', newline='') as file:
            reader = csv.reader(file)
            names = list_utils.strip_all(next(reader))
            form_code_index = list_utils.find_index(
                names, COLUMN_NAMES[Field.TEST_FORM_CODE])
            first_answer_index = list_utils.find_index(names, "Q1")
            for form in reader:
                stripped_form = list_utils.strip_all(form)
                form_code = stripped_form[form_code_index]
                to_order_zero_ind = [
                    int(n) - 1 for n in stripped_form[first_answer_index:]
                ]
                order_map[form_code] = to_order_zero_ind

        sheet_form_code_index = list_utils.find_index(
            self.data[0], COLUMN_NAMES[Field.TEST_FORM_CODE])
        sheet_first_answer_index = list_utils.find_index(self.data[0], "Q1")
        rearranged = [self.data[0]]

        for row in self.data[1:]:
            original_form_code = row[sheet_form_code_index]
            try:
                order_map[original_form_code]
            except KeyError:
                raise ValueError(
                    f"Arrangement file is missing entry for key '{original_form_code}'."
                )
            else:
                row_reordered = row[:sheet_first_answer_index] + [
                    row[ind + sheet_first_answer_index]
                    for ind in order_map[original_form_code]
                ]
                row_reordered[sheet_form_code_index] = ""
                rearranged.append(row_reordered)

        self.data = rearranged
