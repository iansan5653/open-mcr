from datetime import datetime
import time
import typing
import textwrap

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

user_input = user_interface.MainWindow()
input_folder = user_input.input_folder
image_paths = file_handling.filter_images(
    file_handling.list_file_paths(input_folder))
output_folder = user_input.output_folder
multi_answers_as_f = user_input.multi_answers_as_f
empty_answers_as_g = user_input.empty_answers_as_g
keys_file = user_input.keys_file
arrangement_file = user_input.arrangement_file
sort_results = user_input.sort_results
debug_mode_on = user_input.debug_mode

progress = user_interface.ProgressTracker(user_input.root, len(image_paths))

files_timestamp = datetime.now().replace(microsecond=0)

debug_dir = output_folder / (
    data_exporting.format_timestamp_for_file(files_timestamp) + "__debug")
if debug_mode_on:
    data_exporting.make_dir_if_not_exists(debug_dir)

try:
    for image_path in image_paths:
        if debug_mode_on:
            debug_path = debug_dir / image_path.stem
            data_exporting.make_dir_if_not_exists(debug_path)
        else:
            debug_path = None

        progress.set_status(f"Processing '{image_path.name}'.")
        image = image_utils.get_image(image_path, save_path=debug_path)
        prepared_image = image_utils.prepare_scan_for_processing(
            image, save_path=debug_path)

        # Find the corners, skipping the image on failure
        try:
            corners = corner_finding.find_corner_marks(prepared_image,
                                                       save_path=debug_path)
        except corner_finding.CornerFindingError:
            progress.set_status(
                f"Error with '{image_path.name}': couldn't find corners. Skipping..."
            )
            time.sleep(1)
            continue

        # Dilates the image - removes black pixels from edges, which preserves
        # solid shapes while destroying nonsolid ones. By doing this after noise
        # removal and thresholding, it eliminates irregular things like W and M
        morphed_image = image_utils.dilate(prepared_image,
                                           save_path=debug_path)

        # Establish a grid
        grid = grid_r.Grid(corners,
                           grid_i.GRID_HORIZONTAL_CELLS,
                           grid_i.GRID_VERTICAL_CELLS,
                           morphed_image,
                           save_path=debug_path)
        # Calculate the fill threshold
        threshold = grid_r.calculate_bubble_fill_threshold(
            grid, save_path=debug_path)

        # Get the answers for questions
        answers = [
            grid_r.read_answer_as_string(i, grid, multi_answers_as_f,
                                         threshold)
            for i in range(grid_i.NUM_QUESTIONS)
        ]

        field_data: typing.Dict[grid_i.Field, str] = {}

        # Read the last name. If it indicates this exam is a key, treat it as such
        last_name = grid_r.read_field_as_string(grid_i.Field.LAST_NAME, grid,
                                                threshold)
        if last_name == grid_i.KEY_LAST_NAME:
            form_code_field = grid_i.Field.TEST_FORM_CODE
            field_data[form_code_field] = grid_r.read_field_as_string(
                form_code_field, grid, threshold)
            keys_results.add(field_data, answers)
        else:
            field_data[grid_i.Field.LAST_NAME] = last_name
            for field in grid_i.Field:
                # Avoids re-reading the last name value to save some time
                if field is not grid_i.Field.LAST_NAME:
                    field_data[field] = grid_r.read_field_as_string(
                        field, grid, threshold)
            answers_results.add(field_data, answers)
        progress.step_progress()

    answers_results.clean_up(
        replace_empty_with="G" if empty_answers_as_g else "")
    answers_results.save(output_folder,
                         "results",
                         sort_results,
                         timestamp=files_timestamp)

    success_string = "✔️ All exams processed and saved.\n"

    if keys_file:
        keys_results.add_file(keys_file)

    if (keys_results.row_count != 0):
        keys_path = keys_results.save(output_folder,
                                      "keys",
                                      sort_results,
                                      timestamp=files_timestamp)
        success_string += "✔️ All keys processed and saved.\n"
        scores = scoring.score_results(answers_results, keys_results)
        scores.save(output_folder,
                    "scores",
                    sort_results,
                    timestamp=files_timestamp)
        success_string += "✔️ All scored results processed and saved."
        if arrangement_file:
            data_exporting.save_reordered_version(scores,
                                                  arrangement_file,
                                                  output_folder,
                                                  "reordered",
                                                  timestamp=files_timestamp)
            success_string += "✔️ Reordered results saved."
    else:
        success_string += "No exam keys were found, so no scoring was performed."

    progress.set_status(success_string, False)
except Exception as e:
    wrapped_err = "\n".join(textwrap.wrap(str(e), 70))
    progress.set_status(f"Error: {wrapped_err}", False)
    if debug_mode_on:
        raise
progress.show_exit_button_and_wait()
