import time
import typing

import corner_finding
import data_exporting
import file_handling
import grid_info as grid_i
import grid_reading as grid_r
import image_utils
import scoring
import user_interface

answers_results = data_exporting.OutputSheet([x for x in grid_i.Field])
keys_results = data_exporting.OutputSheet([grid_i.Field.TEST_FORM_CODE])

folders_prompt = user_interface.MainWindow()
input_folder = folders_prompt.input_folder
image_paths = file_handling.filter_images(file_handling.list_file_paths(input_folder))
output_folder = folders_prompt.output_folder
multi_answers_as_f = folders_prompt.multi_answers_as_f
keys_file = folders_prompt.keys_file
arrangement_file = folders_prompt.arrangement_file

progress = user_interface.ProgressTracker(folders_prompt.root, len(image_paths))

for image_path in image_paths:
    progress.set_status(f"Processing '{image_path.name}'.")
    image = image_utils.get_image(image_path)
    prepared_image = image_utils.prepare_scan_for_processing(image)

    # Find the corners, skipping the image on failure
    try:
        corners = corner_finding.find_corner_marks(prepared_image)
    except corner_finding.CornerFindingError:
        progress.set_status(f"Error with '{image_path.name}': couldn't find corners. Skipping...")
        time.sleep(1)
        continue

    # Establish a grid
    grid = grid_r.Grid(corners, grid_i.GRID_HORIZONTAL_CELLS,
                       grid_i.GRID_VERTICAL_CELLS, prepared_image)

    # Get the answers for questions
    answers = [
        grid_r.read_answer_as_string(i, grid, multi_answers_as_f)
        for i in range(grid_i.NUM_QUESTIONS)
    ]

    field_data: typing.Dict[grid_i.Field, str] = {}

    # Read the last name. If it indicates this exam is a key, treat it as such
    last_name = grid_r.read_field_as_string(grid_i.Field.LAST_NAME, grid)
    if last_name == grid_i.KEY_LAST_NAME:
        form_code_field = grid_i.Field.TEST_FORM_CODE
        field_data[form_code_field] = grid_r.read_field_as_string(
            form_code_field, grid)
        keys_results.add(field_data, answers)
    else:
        field_data[grid_i.Field.LAST_NAME] = last_name
        for field in grid_i.Field:
            # Avoids re-reading the last name value to save some time
            if field is not grid_i.Field.LAST_NAME:
                field_data[field] = grid_r.read_field_as_string(field, grid)
        answers_results.add(field_data, answers)
    progress.step_progress()

answers_results.save(output_folder / "results.csv")

success_string = "✔️ All exams processed and saved to 'results.csv'.\n"

if keys_file:
    keys_results.add_file(keys_file)

if (keys_results.row_count != 0):
    keys_results.save(output_folder / "keys.csv")
    success_string += "✔️ All keys processed and saved to 'keys.csv'.\n"
    scores = scoring.score_results(answers_results, keys_results)
    scores.save(output_folder / "scores.csv")
    success_string += "✔️ All scored results processed and saved to 'scores.csv'."
    if arrangement_file:
        data_exporting.save_reordered_version(scores, arrangement_file, output_folder / "reordered.csv")
        success_string += "✔️ Reordered results saved to 'reordered.csv'."
else:
    success_string += "No exam keys were found, so no scoring was performed."

progress.set_status(success_string, False)
progress.show_exit_button_and_wait()
