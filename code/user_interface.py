import tkinter as tk
from tkinter import filedialog, ttk
import pathlib
import typing
import str_utils
import ctypes
import file_handling

PADDING = 15
APP_NAME = "Bubble Sheet Reader"


def prompt_folder(message: str, default: str = "./") -> pathlib.Path:
    folderpath = filedialog.askdirectory(initialdir=default, title=message)
    return pathlib.Path(folderpath)


class FolderPickerWidget():
    """sdfgsdfg"""

    onchange: typing.Optional[typing.Callable]
    frame: tk.Frame
    display_text: tk.StringVar
    selected_folder: typing.Optional[pathlib.Path] = None

    def __init__(self,
                 root: tk.Tk,
                 onchange: typing.Optional[typing.Callable] = None):
        self.onchange = onchange

        internal_padding = int(PADDING * 0.66)
        external_padding = PADDING
        pack_opts = {"side": tk.LEFT, "pady": external_padding}

        self.frame = tk.Frame(root)

        self.browse_button = ttk.Button(self.frame,
                                        text="Browse",
                                        command=self.callback,
                                        padding=internal_padding)
        self.browse_button.pack(**pack_opts, padx=(external_padding, 0))

        self.display_text = tk.StringVar()
        selected_file_label = ttk.Label(self.frame,
                                        textvariable=self.display_text,
                                        width=40,
                                        justify=tk.LEFT,
                                        anchor="w",
                                        borderwidth=2,
                                        relief="groove",
                                        padding=internal_padding)
        self.display_text.set("No Folder Selected")
        selected_file_label.pack(**pack_opts, padx=external_padding)

    def pack(self):
        self.frame.pack()

    def callback(self):
        self.selected_folder = prompt_folder("Select Folder")
        self.display_text.set(
            str_utils.shorten_by_cutting_middle(str(self.selected_folder), 45,
                                                3))
        if self.onchange is not None:
            self.onchange()

    def disable(self):
        self.browse_button.configure(state=tk.DISABLED)


class MainWindow:
    input_folder: pathlib.Path
    output_folder: pathlib.Path

    def __init__(self):
        app: tk.Tk = tk.Tk()
        app.title(f"{APP_NAME} - Select Inputs")
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
            app.tk.call('tk', 'scaling', 3.0)
        except Exception:
            pass

        pad_opts = {"padx": PADDING, "pady": PADDING}
        label_opts = {"justify": tk.LEFT, "anchor": "w"}
        heading_opts = {**label_opts, "font": "TkDefaultFont 12 bold"}
        label_pack_opts = {"fill": tk.X, "expand": 1, **pad_opts}
        heading_pack_opts = {**label_pack_opts, "pady": (PADDING * 2, 0)}

        input_folder_heading = ttk.Label(app,
                                         text="Select Input Folder",
                                         **heading_opts)
        input_folder_heading.pack(**heading_pack_opts)
        input_folder_helptext = ttk.Label(
            app,
            text=
            "Select a folder containing the scanned filled bubble sheets.\nAll image files in the selected folder will be processed.",
            **label_opts)
        input_folder_helptext.pack(**label_pack_opts)

        self.input_folder_picker = FolderPickerWidget(app, self.update_status)
        self.input_folder_picker.pack()

        output_folder_heading = ttk.Label(app,
                                          text="Select Output Folder",
                                          **heading_opts)
        output_folder_heading.pack(**heading_pack_opts)
        output_folder_helptext = ttk.Label(
            app,
            text=
            "Select a folder to save output files to.\nExisting files may be overwritten, so it's best to use an empty folder.",
            **label_opts)
        output_folder_helptext.pack(**label_pack_opts)

        self.output_folder_picker = FolderPickerWidget(app, self.update_status)
        self.output_folder_picker.pack()

        self.status_text = tk.StringVar()
        status = tk.Label(app, textvariable=self.status_text)
        status.pack(**heading_pack_opts)
        self.update_status()

        self.confirm_button = ttk.Button(app,
                                         text="Continue",
                                         command=self.confirm,
                                         state=tk.DISABLED)
        self.confirm_button.pack(**pad_opts)

        self.ready_to_continue = tk.IntVar(name="Ready to Close")
        app.wait_variable("Ready to Close")

    def update_status(self):
        ok_to_submit = True
        new_status = ""

        input_folder = self.input_folder_picker.selected_folder
        if input_folder is None:
            new_status += "⚠ Input folder is required.\n"
            ok_to_submit = False
        else:
            self.input_folder = input_folder
            images = file_handling.filter_images(
                file_handling.list_file_paths(input_folder))
            if len(images) == 0:
                new_status += "❌ No image files found in selected input folder.\n"
                ok_to_submit = False
            else:
                new_status += f"✔ Input folder selected. {len(images)} image files found.\n"

        output_folder = self.output_folder_picker.selected_folder
        if output_folder is None:
            new_status += "⚠ Output folder is required.\n"
            ok_to_submit = False
        else:
            self.output_folder = output_folder
            existing_csv_files = file_handling.filter_by_extensions(
                file_handling.list_file_paths(output_folder), [".csv"])
            if len(existing_csv_files) == 0:
                new_status += f"✔ Output folder selected.\n"
            else:
                new_status += f"⚠ Output folder selected. Existing CSV files may be overwritten.\n"
        self.status_text.set(new_status)
        if ok_to_submit:
            self.confirm_button.configure(state=tk.NORMAL)
        return ok_to_submit

    def disable_all(self):
        self.confirm_button.configure(statue=tk.DISABLED)
        self.input_folder_picker.disable()
        self.output_folder_picker.disable()

    def confirm(self):
        if self.update_status():
            self.disable_all()
            self.ready_to_continue.set(1)
