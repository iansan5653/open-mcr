import image_utils
import corner_finding
import grid_reading
import grid_info
from grid_info import fields_info, Field
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
    print(f"Processed '{image_path.name}' successfully.")

results.save(input_directory / "output.csv")
print(f"Results saved to {str(input_directory / 'output.csv')}")
