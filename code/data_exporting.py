""""""
import typing
import csv
from grid_info import Field, NUM_QUESTIONS
from collections import OrderedDict
import pathlib

# The column names, in order
COLUMNS: typing.OrderedDict[Field, str] = OrderedDict()
COLUMNS[Field.LAST_NAME] = "Last Name"
COLUMNS[Field.FIRST_NAME] = "First Name"
COLUMNS[Field.MIDDLE_NAME] = "Middle Name"
COLUMNS[Field.STUDENT_ID] = "Student ID"
COLUMNS[Field.COURSE_ID] = "Course ID"
COLUMNS[Field.TEST_FORM_CODE] = "Test Form Code"


def field_group_to_string(values: typing.List[typing.Union[typing.List[str], typing.List[int]]]):
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


class OutputSheet:
    data: typing.List[typing.List[str]]

    def __init__(self):
        field_columns = list(COLUMNS.values())
        answer_columns = [str(i + 1) for i in range(NUM_QUESTIONS)]
        self.data = [field_columns + answer_columns]

    def save(self, path: pathlib.PurePath):
        with open(str(path), 'w+', newline='') as output_file:
            writer = csv.writer(output_file)
            writer.writerows(self.data)

    def add(self, fields: typing.Dict[Field, str], answers: typing.List[str]):
        row: typing.List[str] = []
        for column in COLUMNS.keys():
            try:
                row.append(fields[column])
            except KeyError:
                row.append('')
        self.data.append(row + answers)
