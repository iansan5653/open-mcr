import pathlib
import image_utils
import corner_finding
import grid_reading
import grid_info
from grid_info import fields_info, Field
import data_exporting

images = [str(i) + ".jpg" for i in range(1, 11)]

results = data_exporting.OutputSheet()

folder = pathlib.Path(
    "C:\\Users\\Ian Sanders\\Git Repositories\\scantron-reading\\examples\\")
for image_name in images:
    image_path = folder / image_name
    image = image_utils.get_image(image_path)
    prepared_image = image_utils.prepare_scan_for_processing(image)
    try:
        corners = corner_finding.find_corner_marks(prepared_image)
    except RuntimeError:
        print(f"{image_name}: Can't find corners.")
        continue
    grid = grid_reading.Grid(corners, 36, 48, prepared_image)
    field_data = {
        field: data_exporting.field_group_to_string(
            fields_info[field].get_group(grid).read_value())
        for field in Field
    }
    answers = [
        data_exporting.field_group_to_string(
            question.get_group(grid).read_value())
        for question in grid_info.questions_info
    ]
    results.add(field_data, answers)

results.save(folder / "output.csv")
print(f"Results saved to {str(folder / 'output.csv')}")
