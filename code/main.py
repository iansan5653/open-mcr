import pathlib
import image_utils
import corner_finding
import grid_reading

images = [str(i) + ".jpg" for i in range(1, 11)]

last_name_info = grid_reading.GridGroupInfo(1, 3, 12, grid_reading.FieldType.LETTER)
first_name_info = grid_reading.GridGroupInfo(14, 3, 6, grid_reading.FieldType.LETTER)
middle_name_info = grid_reading.GridGroupInfo(21, 3, 2, grid_reading.FieldType.LETTER)
student_id_info = grid_reading.GridGroupInfo(25, 3, 10)
course_id_info = grid_reading.GridGroupInfo(25, 16, 10)

folder = pathlib.Path(
    "C:\\Users\\Ian Sanders\\Git Repositories\\scantron-reading\\examples\\")
for image_name in images:
    image_path = folder / image_name
    image = image_utils.get_image(image_path)
    try:
        corners = corner_finding.find_corner_marks(image)
    except RuntimeError:
        print(f"{image_name}: Can't find corners.")
        continue
    image_bw = image_utils.convert_to_bw(image)
    grid = grid_reading.Grid(corners, 36, 51, image_bw)
    last_name_group = last_name_info.get_group(grid)
    student_id_group = student_id_info.get_group(grid)
    last_name = last_name_group.read_value()
    student_id = student_id_group.read_value()
    print(f"{image_name}:\n\t{last_name}\n\t{student_id}")
