import abc
import pathlib
import sys
import tkinter as tk
import typing
from tkinter import filedialog, ttk
import subprocess

import file_handling
import str_utils
import scoring

YPADDING = 4
XPADDING = 7
APP_NAME = "OpenMCR"


def prompt_folder(message: str = "Select Folder",
                  default: str = "./") -> pathlib.Path:
    folderpath = filedialog.askdirectory(initialdir=default, title=message)
    return pathlib.Path(folderpath)


def prompt_file(
        message: str = "Select File",
        default: str = "./",
        filetypes: typing.Optional[typing.List[typing.Tuple[str, str]]] = None
) -> pathlib.Path:
    filepath = filedialog.askopenfilename(initialdir=default,
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
    font_opt = {"font": "TkDefaultFont 10 bold"} if heading else {}
    pady_opt = {"pady": (YPADDING * 2, 0)} if heading else {"pady": YPADDING}
    label = ttk.Label(root, text=text, justify=tk.LEFT, anchor="w", **font_opt)
    return pack(label, fill=tk.X, expand=1, padx=XPADDING, **pady_opt)


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
        self.emptytext = emptytext

        internal_padding = int(XPADDING * 0.66)
        external_padding = XPADDING
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

    def update_display_text(self, selection: typing.Optional[pathlib.Path]):
        display_text = str_utils.trim_middle_to_len(
            str(selection), 45, 3) if selection is not None else self.emptytext
        self.display_text.set(display_text)
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
        selection = prompt_folder()
        self.selection = selection if str(selection).strip() != "." else None
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
        selection = prompt_file(filetypes=self.__filetypes)
        self.selection = selection if str(selection).strip() != "." else None
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
                 onchange: typing.Optional[typing.Callable] = None,
                 reduce_padding_above: bool = False):
        self.onchange = onchange
        self.checked = tk.IntVar(root, 0)

        internal_padding = int(XPADDING * 0.33)
        external_padding = XPADDING
        top_padding = external_padding if not reduce_padding_above else 0
        pack_opts = {"side": tk.LEFT, "pady": (top_padding, external_padding)}

        self.frame = tk.Frame(root)
        self.checkbox = pack(ttk.Checkbutton(self.frame,
                                             text=label,
                                             command=self.callback,
                                             variable=self.checked,
                                             padding=internal_padding,
                                             width=50),
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
    multi_answers_as_f: bool
    empty_answers_as_g: bool
    keys_file: typing.Optional[pathlib.Path]
    arrangement_file: typing.Optional[pathlib.Path]
    sort_results: bool

    def __init__(self):
        app: tk.Tk = tk.Tk()
        self.root = app
        app.title(f"{APP_NAME} - Select Inputs")

        iconpath = str(pathlib.Path(__file__).parent / "assets" / "icon.ico")
        app.iconbitmap(iconpath)

        self.keys_file = None
        self.arrangement_file = None

        create_and_pack_label(app, "Select Input Folder", heading=True)
        create_and_pack_label(
            app,
            "Select a folder containing the scanned multiple choice sheets.\nSheets with last name of 'ZZZZZZZZZZZZ' will be treated as keys.\nAll image files in the selected folder will be processed, ignoring subfolders."
        )

        self.__input_folder_picker = FolderPickerWidget(
            app, self.update_status)
        self.__multi_answers_as_f_checkbox = CheckboxWidget(
            app, "Convert multiple answers in a question to 'F'.",
            self.update_status)
        self.__empty_answers_as_g_checkbox = CheckboxWidget(
            app, "Save empty answers in questions as 'G'.", self.update_status,
            True)

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
        self.__sort_results_checkbox = CheckboxWidget(app,
                                                      "Sort results by name",
                                                      self.update_status)

        self.__status_text = tk.StringVar()
        status = tk.Label(app, textvariable=self.__status_text)
        status.pack(fill=tk.X, expand=1, pady=(YPADDING * 2, 0))
        self.update_status()

        buttons_frame = tk.Frame(app)
        self.__sheet_button = pack(ttk.Button(buttons_frame,
                                              text="Open Sheet",
                                              command=self.show_sheet),
                                   padx=XPADDING,
                                   pady=YPADDING,
                                   side=tk.LEFT)
        self.__help_button = pack(ttk.Button(buttons_frame,
                                             text="Open Help",
                                             command=self.show_help),
                                  padx=XPADDING,
                                  pady=YPADDING,
                                  side=tk.LEFT)
        self.__confirm_button = pack(ttk.Button(buttons_frame,
                                                text="✔ Continue",
                                                command=self.confirm,
                                                state=tk.DISABLED),
                                     padx=XPADDING,
                                     pady=YPADDING,
                                     side=tk.RIGHT)
        pack(buttons_frame, fill=tk.X, expand=1)

        self.__ready_to_continue = tk.IntVar(name="Ready to Continue")
        app.wait_variable("Ready to Continue")

    def update_status(self):
        ok_to_submit = True
        new_status = ""

        input_folder = self.__input_folder_picker.selection
        if input_folder is None:
            new_status += "❌ Input folder is required.\n"
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
            new_status += "❌ Output folder is required.\n"
            ok_to_submit = False
        else:
            self.output_folder = output_folder
            existing_csv_files = file_handling.filter_by_extensions(
                file_handling.list_file_paths(output_folder), [".csv"])
            if len(existing_csv_files) == 0:
                new_status += f"✔ Output folder selected.\n"
            else:
                new_status += f"✔⚠ Output folder selected. Existing CSV files may be overwritten.\n"

        keys_file = self.__answer_key_picker.selection
        if keys_file:
            if scoring.verify_answer_key_sheet(keys_file):
                self.keys_file = keys_file
                new_status += f"✔ Selected answer keys file appears to be valid.\n"
            else:
                self.keys_file = None
                new_status += f"❌ Selected answer keys file is not valid.\n"
                ok_to_submit = False

        arrangement_file = self.__key_arrangement_picker.selection
        if arrangement_file:
            if scoring.verify_answer_key_sheet(arrangement_file):
                self.arrangement_file = arrangement_file
                new_status += f"✔ Selected key arrangement file appears to be valid.\n"
            else:
                self.arrangement_file = None
                new_status += f"❌ Selected key arrangement file is not valid.\n"
                ok_to_submit = False

        self.multi_answers_as_f = bool(
            self.__multi_answers_as_f_checkbox.checked.get())
        if self.multi_answers_as_f:
            new_status += f"Questions with multiple answers selected will be output as 'F'.\n"
        else:
            new_status += f"Questions with multiple answers selected will be output in '[A|B]' form.\n"

        self.empty_answers_as_g = bool(
            self.__empty_answers_as_g_checkbox.checked.get())
        if self.empty_answers_as_g:
            new_status += f"Unanswered questions will be output as 'G'.\n"
        else:
            new_status += f"Unanswered questions will be left as blank cells.\n"

        self.sort_results = bool(self.__sort_results_checkbox.checked.get())
        if self.sort_results:
            new_status += f"Results will be sorted by name.\n"
        else:
            new_status += f"Results will be left in original order.\n"

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
        self.__empty_answers_as_g_checkbox.disable()
        self.__sort_results_checkbox.disable()

    def confirm(self):
        if self.update_status():
            self.disable_all()
            self.__ready_to_continue.set(1)

    def show_help(self):
        helpfile = str(pathlib.Path(__file__).parent / "assets" / "manual.pdf")
        subprocess.Popen([helpfile], shell=True)

    def show_sheet(self):
        helpfile = str(
            pathlib.Path(__file__).parent / "assets" /
            "multiple_choice_sheet.pdf")
        subprocess.Popen([helpfile], shell=True)


class ProgressTracker:
    def __init__(self, parent: tk.Tk, maximum: int):
        self.maximum = maximum
        self.value = 0
        self.parent = parent
        pack_opts = {
            "fill": tk.X,
            "expand": 1,
            "padx": XPADDING,
            "pady": YPADDING
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
        close_button.pack(padx=XPADDING, pady=YPADDING)
        close_button.wait_variable("Ready to Close")
        sys.exit(0)
