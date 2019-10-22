import abc
import ctypes
import pathlib
import sys
import tkinter as tk
import typing
from tkinter import filedialog, ttk
import subprocess

import file_handling
import str_utils

PADDING = 15
APP_NAME = "Bubble Sheet Reader"


def prompt_folder(message: str = "Select Folder",
                  default: str = "./") -> pathlib.Path:
    folderpath = filedialog.askdirectory(initialdir=default, title=message)
    return pathlib.Path(folderpath)


def prompt_file(
        message: str = "Select File",
        default: str = "./",
        filetypes: typing.Optional[typing.List[typing.Tuple[str, str]]] = None
) -> pathlib.Path:
    filepath = filedialog.askopenfile(initialdir=default,
                                      title=message,
                                      filetypes=filetypes)
    return pathlib.Path(filepath)


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


class PickerWidget(abc.ABC):
    """File picker widget (browse button and file path)."""

    onchange: typing.Optional[typing.Callable]
    frame: tk.Frame
    browse_button: ttk.Button
    display_text: tk.StringVar
    selection: typing.Optional[pathlib.Path] = None

    def __init__(self,
                 root: tk.Tk,
                 emptytext: str,
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
        self.display_text.set(emptytext)
        self.frame.pack()

    @abc.abstractmethod
    def callback(self):
        ...

    def update_display_text(self, selection: pathlib.Path):
        self.display_text.set(
            str_utils.trim_middle_to_len(str(selection), 45, 3))
        if self.onchange is not None:
            self.onchange()

    def disable(self):
        self.browse_button.configure(state=tk.DISABLED)


class FolderPickerWidget(PickerWidget):
    def __init__(self,
                 root: tk.Tk,
                 onchange: typing.Optional[typing.Callable] = None):
        super().__init__(root, "No Folder Selected", onchange)

    def callback(self):
        self.selection = prompt_folder()
        self.update_display_text(self.selection)


class FilePickerWidget(PickerWidget):
    def __init__(self,
                 root: tk.Tk,
                 filetypes: typing.Optional[typing.List[
                     typing.Tuple[str, str]]] = None,
                 onchange: typing.Optional[typing.Callable] = None):
        self.__filetypes = filetypes
        super().__init__(root, "No File Selected", onchange)

    def callback(self):
        self.selection = prompt_file(filetypes=self.__filetypes)
        self.update_display_text(self.selection)


class CheckboxWidget:
    """File picker widget (browse button and file path)."""

    onchange: typing.Optional[typing.Callable]
    frame: tk.Frame
    checkbox: ttk.Checkbutton
    checked: tk.IntVar

    def __init__(self,
                 root: tk.Tk,
                 label: str,
                 onchange: typing.Optional[typing.Callable] = None):
        self.onchange = onchange
        self.checked = tk.IntVar(root, 0)

        internal_padding = int(PADDING * 0.66)
        external_padding = PADDING
        pack_opts = {"side": tk.LEFT, "pady": external_padding}

        self.frame = tk.Frame(root)
        self.checkbox = pack(ttk.Checkbutton(self.frame,
                                             text=label,
                                             command=self.callback,
                                             variable=self.checked,
                                             padding=internal_padding,
                                             width=45),
                             **pack_opts,
                             padx=(external_padding, 0))
        self.frame.pack()

    def callback(self):
        if self.onchange is not None:
            self.onchange()

    def disable(self):
        self.checkbox.configure(state=tk.DISABLED)


class MainWindow:
    root: tk.Tk
    input_folder: pathlib.Path
    output_folder: pathlib.Path

    def __init__(self):
        app: tk.Tk = tk.Tk()
        self.root = app
        app.title(f"{APP_NAME} - Select Inputs")

        iconpath = str(pathlib.Path(__file__).parent / "icon.ico")
        app.iconbitmap(iconpath)

        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
            app.tk.call('tk', 'scaling', 3.0)
        except Exception:
            pass

        create_and_pack_label(app, "Select Input Folder", heading=True)
        create_and_pack_label(
            app,
            "Select a folder containing the scanned filled bubble sheets.\nSheets with last name of 'ZZZZZZZZZZZZ' will be treated as keys.\nAll image files in the selected folder will be processed.\nSubfolders will be ignored."
        )

        self.__input_folder_picker = FolderPickerWidget(
            app, self.update_status)
        self.__multi_answers_as_f_checkbox = CheckboxWidget(
            app, "Convert multiple answers in a question to 'F'.", self.update_status)

        create_and_pack_label(app,
                              "Select Answer Keys File (Optional)",
                              heading=True)
        create_and_pack_label(
            app,
            "Select a CSV file containing the answer keys.\nIf provided, these keys will be used over any keys found in sheets.\nSee 'Help' for formatting instructions."
        )

        self.__answer_key_picker = FilePickerWidget(app,
                                                    [("CSV Files", "*.csv")],
                                                    self.update_status)

        create_and_pack_label(app,
                              "Select Keys Arrangement File (Optional)",
                              heading=True)
        create_and_pack_label(
            app,
            "Select a CSV file containing information about the relative order of each key.\nIf provided, a reordered version will be included in the output.\nSee 'Help' for formatting instructions."
        )

        self.__key_arrangement_picker = FilePickerWidget(
            app, [("CSV Files", "*.csv")], self.update_status)

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

        buttons_frame = tk.Frame(app)
        self.__help_button = pack(ttk.Button(buttons_frame,
                                             text="Help",
                                             command=self.show_help),
                                  padx=PADDING,
                                  pady=PADDING,
                                  side=tk.LEFT)
        self.__confirm_button = pack(ttk.Button(buttons_frame,
                                                text="Continue",
                                                command=self.confirm,
                                                state=tk.DISABLED),
                                     padx=PADDING,
                                     pady=PADDING,
                                     side=tk.LEFT)
        pack(buttons_frame)

        self.__ready_to_continue = tk.IntVar(name="Ready to Continue")
        app.wait_variable("Ready to Continue")

    def update_status(self):
        ok_to_submit = True
        new_status = ""

        input_folder = self.__input_folder_picker.selection
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

        output_folder = self.__output_folder_picker.selection
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

        self.multi_answers_as_f = self.__multi_answers_as_f_checkbox.checked.get()
        if self.multi_answers_as_f:
            new_status += f"Questions with multiple answers selected will have output as 'F'.\n"
        else:
            new_status += f"Questions with multiple answers selected will have output in '[A|B]' form.\n"

        self.__status_text.set(new_status)
        if ok_to_submit:
            self.__confirm_button.configure(state=tk.NORMAL)
        return ok_to_submit

    def disable_all(self):
        self.__confirm_button.configure(state=tk.DISABLED)
        self.__input_folder_picker.disable()
        self.__output_folder_picker.disable()
        self.__answer_key_picker.disable()
        self.__key_arrangement_picker.disable()
        self.__multi_answers_as_f_checkbox.disable()

    def confirm(self):
        if self.update_status():
            self.disable_all()
            self.__ready_to_continue.set(1)

    def show_help(self):
        print(pathlib.Path(__file__).parent / "manual.pdf")
        helpfile = str(pathlib.Path(__file__).parent / "manual.pdf")
        subprocess.Popen([helpfile], shell=True)


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
