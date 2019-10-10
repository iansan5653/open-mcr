""""""
import typing
import csv
from grid_info import Field, NUM_QUESTIONS
import pathlib

COLUMN_NAMES: typing.Dict[Field, str] = {
    Field.LAST_NAME: "Last Name",
    Field.FIRST_NAME: "First Name",
    Field.MIDDLE_NAME: "Middle Name",
    Field.STUDENT_ID: "Student ID",
    Field.COURSE_ID: "Course ID",
    Field.TEST_FORM_CODE: "Test Form Code"
}


def field_group_to_string(
        values: typing.List[typing.Union[typing.List[str], typing.List[int]]]):
    result_strings: typing.List[str] = []
    for value in values:
        if len(value) == 0:
            result_strings.append(' ')
        elif len(value) == 1:
            result_strings.append(str(value[0]))
        else:
            value_as_strings = [str(el) for el in value]
            result_strings.append(f'[{"|".join(value_as_strings)}]')
    return "".join(result_strings).strip()


class OutputSheet():
    """A lightweight matrix of data to be exported. Faster than a dataframe but
    can be easily converted to one when the need arises."""
    # Must be structured as: field_a, field_b, ..., 1, 2, 3, ...
    data: typing.List[typing.List[str]]
    __field_columns: typing.List[Field]
    row_count: int

    def __init__(self, columns: typing.List[Field]):
        self.__field_columns = columns
        field_column_names = [COLUMN_NAMES[column] for column in columns]
        answer_columns = [str(i + 1) for i in range(NUM_QUESTIONS)]
        self.data = [field_column_names + answer_columns]
        self.row_count = 0

    def save(self, path: pathlib.PurePath):
        with open(str(path), 'w+', newline='') as output_file:
            writer = csv.writer(output_file)
            writer.writerows(self.data)

    def add(self, fields: typing.Dict[Field, str], answers: typing.List[str]):
        row: typing.List[str] = []
        for column in self.__field_columns:
            try:
                row.append(fields[column])
            except KeyError:
                row.append('')
        self.data.append(row + answers)
        self.row_count = len(self.data) - 1
