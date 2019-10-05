from geometry_utils import Orientation
from grid_reading import GridGroupInfo, FieldType
import enum
import typing

NUM_QUESTIONS = 75


class Field(enum.Enum):
    LAST_NAME = enum.auto()
    FIRST_NAME = enum.auto()
    MIDDLE_NAME = enum.auto()
    STUDENT_ID = enum.auto()
    COURSE_ID = enum.auto()
    TEST_FORM_CODE = enum.auto()


fields_info: typing.Dict[Field, GridGroupInfo] = {
    Field.LAST_NAME:
    GridGroupInfo(1, 3, 12, fields_type=FieldType.LETTER),
    Field.FIRST_NAME:
    GridGroupInfo(14, 3, 6, fields_type=FieldType.LETTER),
    Field.MIDDLE_NAME:
    GridGroupInfo(21, 3, 2, fields_type=FieldType.LETTER),
    Field.STUDENT_ID:
    GridGroupInfo(25, 3, 10),
    Field.COURSE_ID:
    GridGroupInfo(25, 16, 10),
    Field.TEST_FORM_CODE:
    GridGroupInfo(27,
                  28,
                  fields_type=FieldType.LETTER,
                  field_length=6,
                  field_orientation=Orientation.HORIZONTAL)
}

questions_info = [
    GridGroupInfo(2 + (7 * (i // 15)),
                  32 + i - (15 * (i // 15)),
                  fields_type=FieldType.LETTER,
                  field_length=5,
                  field_orientation=Orientation.HORIZONTAL)
    for i in range(NUM_QUESTIONS)
]


class dimensions:
    vertical_cells = 36
    horizontal_cells = 48
