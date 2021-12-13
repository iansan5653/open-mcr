import file_handling
import grid_info as grid_i
import user_interface
import sys
from process_input import process_input
from datetime import datetime

user_input = user_interface.MainWindow()
if (user_input.cancelled):
    sys.exit(0)

input_folder = user_input.input_folder
image_paths = file_handling.filter_images(
    file_handling.list_file_paths(input_folder))
output_folder = user_input.output_folder
multi_answers_as_f = user_input.multi_answers_as_f
empty_answers_as_g = user_input.empty_answers_as_g
keys_file = user_input.keys_file
arrangement_file = user_input.arrangement_map
sort_results = user_input.sort_results
output_mcta = user_input.output_mcta
debug_mode_on = user_input.debug_mode
form_variant = grid_i.form_150q if user_input.form_variant == user_interface.FormVariantSelection.VARIANT_150_Q else grid_i.form_75q
progress_tracker = user_input.create_and_pack_progress(maximum=len(image_paths))
files_timestamp = datetime.now().replace(microsecond=0)

process_input(image_paths,
              output_folder,
              multi_answers_as_f,
              empty_answers_as_g,
              keys_file,
              arrangement_file,
              sort_results,
              output_mcta,
              debug_mode_on,
              form_variant,
              progress_tracker,
              files_timestamp)
