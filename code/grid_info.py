from geometry_utils import Orientation
import enum
import typing
import alphabet

NUM_QUESTIONS = 75
KEY_LAST_NAME = "XXXXXXXXXXXX"
GRID_HORIZONTAL_CELLS = 36
GRID_VERTICAL_CELLS = 48


class Field(enum.Enum):
    """Fields that exist on the bubble sheet."""
    LAST_NAME = enum.auto()
    FIRST_NAME = enum.auto()
    MIDDLE_NAME = enum.auto()
    STUDENT_ID = enum.auto()
    COURSE_ID = enum.auto()
    TEST_FORM_CODE = enum.auto()


class VirtualField(enum.Enum):
    """Data points that don't exist on the bubble sheet, but could be added to the output."""
    SCORE = enum.auto()


RealOrVirtualField = typing.Union[Field, VirtualField]


class FieldType(enum.Enum):
    LETTER = enum.auto()
    NUMBER = enum.auto()


class GridGroupInfo():
    """Metadata about a set of grid cells (not tied to a specific grid or image)."""

    horizontal_start: int
    vertical_start: int
    num_fields: int
    field_length: int
    fields_type: FieldType
    field_orientation: Orientation

    def __init__(self,
                 horizontal_start: int,
                 vertical_start: int,
                 num_fields: int = 1,
                 fields_type: FieldType = FieldType.NUMBER,
                 field_length: typing.Optional[int] = None,
                 field_orientation: Orientation = Orientation.VERTICAL):
        self.horizontal_start = horizontal_start
        self.vertical_start = vertical_start
        self.num_fields = num_fields
        if field_length is not None:
            self.field_length = field_length
        elif fields_type is FieldType.LETTER:
            self.field_length = alphabet.LENGTH
        else:
            self.field_length = 10
        self.fields_type = fields_type
        self.field_orientation = field_orientation


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
