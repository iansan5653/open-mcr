import tkinter as tk
from tkinter import filedialog, ttk
import pathlib
import typing
import str_utils
import ctypes
import file_handling
import sys

PADDING = 15
APP_NAME = "Bubble Sheet Reader"


def prompt_folder(message: str = "Select Folder",
                  default: str = "./") -> pathlib.Path:
    folderpath = filedialog.askdirectory(initialdir=default, title=message)
    return pathlib.Path(folderpath)


T = typing.TypeVar("T", bound=tk.Widget)


def pack(widget: T, *args: typing.Any, **kwargs: typing.Any) -> T:
    """A more convenient way to pack widgets and create them in a single call"""
    widget.pack(*args, **kwargs)
    return widget


def create_and_pack_label(root: tk.Tk, text: str,
                          heading: bool = False) -> ttk.Label:
    font_opt = {"font": "TkDefaultFont 12 bold"} if heading else {}
    pady_opt = {"pady": (PADDING * 2, 0)} if heading else {"pady": PADDING}
    label = ttk.Label(root, text=text, justify=tk.LEFT, anchor="w", **font_opt)
    return pack(label, fill=tk.X, expand=1, padx=PADDING, **pady_opt)


class FolderPickerWidget():
    """File picker widget (browse button and file path)."""

    onchange: typing.Optional[typing.Callable]
    frame: tk.Frame
    browse_button: ttk.Button
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
        self.browse_button = pack(ttk.Button(self.frame,
                                             text="Browse",
                                             command=self.callback,
                                             padding=internal_padding),
                                  **pack_opts,
                                  padx=(external_padding, 0))

        self.display_text = tk.StringVar()
        pack(ttk.Label(self.frame,
                       textvariable=self.display_text,
                       width=40,
                       justify=tk.LEFT,
                       anchor="w",
                       borderwidth=2,
                       relief="groove",
                       padding=internal_padding),
             **pack_opts,
             padx=external_padding)
        self.display_text.set("No Folder Selected")
        self.frame.pack()

    def callback(self):
        self.selected_folder = prompt_folder()
        self.display_text.set(
            str_utils.trim_middle_to_len(str(self.selected_folder), 45, 3))
        if self.onchange is not None:
            self.onchange()

    def disable(self):
        self.browse_button.configure(state=tk.DISABLED)


class MainWindow:
    root: tk.Tk
    input_folder: pathlib.Path
    output_folder: pathlib.Path

    def __init__(self):
        app: tk.Tk = tk.Tk()
        self.root = app
        app.title(f"{APP_NAME} - Select Inputs")
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
            app.tk.call('tk', 'scaling', 3.0)
        except Exception:
            pass

        create_and_pack_label(app, "Select Input Folder", heading=True)
        create_and_pack_label(
            app,
            "Select a folder containing the scanned filled bubble sheets.\nAll image files in the selected folder will be processed."
        )

        self.__input_folder_picker = FolderPickerWidget(
            app, self.update_status)

        create_and_pack_label(app, "Select Output Folder", heading=True)
        create_and_pack_label(
            app,
            "Select a folder to save output files to.\nExisting files may be overwritten, so it's best to use an empty folder."
        )

        self.__output_folder_picker = FolderPickerWidget(
            app, self.update_status)

        self.__status_text = tk.StringVar()
        status = tk.Label(app, textvariable=self.__status_text)
        status.pack(fill=tk.X, expand=1, pady=(PADDING * 2, 0))
        self.update_status()

        self.__confirm_button = pack(ttk.Button(app,
                                                text="Continue",
                                                command=self.confirm,
                                                state=tk.DISABLED),
                                     padx=PADDING,
                                     pady=PADDING)

        self.__ready_to_continue = tk.IntVar(name="Ready to Continue")
        app.wait_variable("Ready to Continue")

    def update_status(self):
        ok_to_submit = True
        new_status = ""

        input_folder = self.__input_folder_picker.selected_folder
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

        output_folder = self.__output_folder_picker.selected_folder
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
        self.__status_text.set(new_status)
        if ok_to_submit:
            self.__confirm_button.configure(state=tk.NORMAL)
        return ok_to_submit

    def disable_all(self):
        self.__confirm_button.configure(state=tk.DISABLED)
        self.__input_folder_picker.disable()
        self.__output_folder_picker.disable()

    def confirm(self):
        if self.update_status():
            self.disable_all()
            self.__ready_to_continue.set(1)


class ProgressTracker:
    def __init__(self, parent: tk.Tk, maximum: int):
        self.maximum = maximum
        self.value = 0
        self.parent = parent
        pack_opts = {
            "fill": tk.X,
            "expand": 1,
            "padx": PADDING,
            "pady": PADDING
        }
        self.status_text = tk.StringVar(parent)
        pack(ttk.Label(parent, textvariable=self.status_text, width=45),
             **pack_opts)
        self.progress_bar = pack(
            ttk.Progressbar(parent, maximum=maximum, mode="determinate"),
            **pack_opts)
        self.close_when_changes = tk.IntVar(parent, name="Ready to Close")

    def step_progress(self, step: int = 1):
        self.value += step
        self.progress_bar.step(step)
        self.parent.update()
        self.parent.update_idletasks()

    def set_status(self, status: str, show_count: bool = True):
        new_status = f"{status} ({self.value}/{self.maximum})" if show_count else status
        self.status_text.set(new_status)

    def set_ready_to_close(self):
        self.close_when_changes.set(1)

    def show_exit_button_and_wait(self):
        close_button = ttk.Button(self.parent,
                                  text="Close",
                                  command=self.set_ready_to_close)
        close_button.pack(padx=PADDING, pady=PADDING)
        close_button.wait_variable("Ready to Close")
        sys.exit(0)
