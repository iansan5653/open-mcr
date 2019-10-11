import image_utils
import corner_finding
import grid_reading
from grid_info import fields_info, Field, KEY_LAST_NAME, read_field_as_string, GRID_HORIZONTAL_CELLS, GRID_VERTICAL_CELLS
import data_exporting
import tkinter as tk
import file_handling

answers_results = data_exporting.OutputSheet([x for x in Field])
keys_results = data_exporting.OutputSheet([Field.TEST_FORM_CODE])

app = tk.Tk()
input_directory = file_handling.prompt_folder(
    "Select a folder to import scans from")
images = file_handling.filter_images(
    file_handling.list_file_paths(input_directory))
output_directory = file_handling.prompt_folder(
    "Select a folder to save results in")
app.destroy()

for image_path in images:
    image = image_utils.get_image(image_path)
    prepared_image = image_utils.prepare_scan_for_processing(image)
    try:
        corners = corner_finding.find_corner_marks(prepared_image)
    except RuntimeError:
        print(f"{image_path.name}: Can't find corners.")
        continue
    grid = grid_reading.Grid(corners, GRID_HORIZONTAL_CELLS, GRID_VERTICAL_CELLS, prepared_image)

    last_name = read_field_as_string(Field.LAST_NAME, grid)
    if last_name == KEY_LAST_NAME:
        field_data = {
            Field.TEST_FORM_CODE: read_field_as_string(Field.TEST_FORM_CODE, grid)
        }
    else:
        field_data = {
            field: data_exporting.field_group_to_string(
                fields_info[field].get_group(grid).read_value())
            for field in Field if field is not Field.LAST_NAME
        }
    answers = [
        data_exporting.field_group_to_string(
            question.get_group(grid).read_value())
        for question in grid_info.questions_info
    ]
    results.add(field_data, answers)
    print(f"Processed '{image_path.name}' successfully.")

results.save(input_directory / "output.csv")
print(f"Results saved to {str(input_directory / 'output.csv')}")
