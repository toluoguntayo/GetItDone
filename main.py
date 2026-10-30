import customtkinter as ctk
import json
import sys
import ctypes
from pathlib import Path
from datetime import datetime
from typing import Callable

if getattr(sys, "frozen", False):
    APP_DIR = Path(sys.executable).parent
else:
    APP_DIR = Path(__file__).parent

def load_custom_fonts():
    font_path = Path(__file__).parent / "assets" / "JetBrainsMono-Bold.ttf"

    if sys.platform == "win32" and font_path.exists():
        ctypes.windll.gdi32.AddFontResourceExW(str(font_path), 0x10, 0)


load_custom_fonts()

TASKS_FILE = APP_DIR / "tasks.json"
FONT_FAMILY = "JetBrains Mono"

def ensure_tasks_file():
    #  Create tasks.json with an empty array if it doesn't exist.
    if not TASKS_FILE.exists():
        TASKS_FILE.write_text("[]", encoding="utf-8")


class Theme:
    # Theme definitions
    BG_MAIN = "#0C0E22"
    BG_CARD = "#0F1028"
    BG_WIDGET = "#161840"
    BORDER = "#252560"
    TEXT = "#EAE8F6"
    TEXT_MUTED = "#9488CC"
    ACCENT = "#6448E4"
    ACCENT_HOVER = "#7860F8"

    TASK_CARD_BG = "#14143A"
    TASK_CARD_HOVER = "#1A1A48"

    BUTTON_PRIMARY_BG = "#6448E4"
    BUTTON_PRIMARY_HOVER = "#7860F8"
    BUTTON_PRIMARY_BORDER = "#2E2A78"
    BUTTON_PRIMARY_TEXT = "#FFFFFF"

    BUTTON_SECONDARY_BG = "#14143A"
    BUTTON_SECONDARY_HOVER = "#1A1A48"
    BUTTON_SECONDARY_BORDER = "#252560"
    BUTTON_SECONDARY_TEXT = "#EAE8F6"

    # Layout constants
    RADIUS_MD = 24
    RADIUS_LG = 28
    RADIUS_BUTTONS = 8
    HEIGHT_MD = 46
    HEIGHT_SM = 54
    BORDER_WIDTH = 1

class TaskWidget(ctk.CTkFrame):
    #  Displays a single task with edit/delete actions.

    def __init__(
        self,
        parent,
        task_text: str,
        task_date: str,
        task_index: int,
        on_edit: Callable,
        on_delete: Callable,
    ):
        super().__init__(
            parent,
            fg_color=Theme.TASK_CARD_BG,
            border_color=Theme.BORDER,
            border_width=Theme.BORDER_WIDTH,
            corner_radius=12,
        )

        self.task_text = task_text
        self.task_index = task_index
        self.on_edit = on_edit
        self.on_delete = on_delete

        self.grid_columnconfigure(0, weight=1)

        app = self.winfo_toplevel()

        self.label = ctk.CTkLabel(
            self,
            text=task_text,
            font=app.FONT_TASK,
            text_color=Theme.TEXT,
            anchor="w",
            justify="left",
            wraplength=360,
        )
        self.label.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=(15, 5),
            pady=(10, 0),
        )

        self.date_label = ctk.CTkLabel(
            self,
            text=task_date,
            font=app.FONT_TIMESTAMP,
            text_color=Theme.TEXT_MUTED,
            anchor="w",
        )
        if task_date:
            self.date_label.grid(
                row=1,
                column=0,
                sticky="ew",
                padx=(15, 5),
                pady=(0, 10),
            )

        self.grid_columnconfigure(1, weight=0)

        self.button_frame = ctk.CTkFrame(
            self,
            fg_color="transparent",
        )
        self.button_frame.grid(
            row=0,
            column=1,
            rowspan=2,
            sticky="e",
            padx=(0, 5),
            pady=10,
        )

        self.edit_button = ctk.CTkButton(
            self.button_frame,
            text="Edit",
            width=80, 
            height=Theme.HEIGHT_SM,
            font=app.FONT_BUTTON,
            fg_color=Theme.BUTTON_SECONDARY_BG,
            hover_color=Theme.BUTTON_SECONDARY_HOVER,
            border_color=Theme.BUTTON_SECONDARY_BORDER,
            border_width=1,
            text_color=Theme.BUTTON_SECONDARY_TEXT,
            corner_radius=8,
            command=lambda: self.on_edit(self.task_index),
        )
        self.edit_button.grid(row=0, column=0, padx=(0, 5))

        self.delete_button = ctk.CTkButton(
            self.button_frame,
            text="Delete",
            width=80,
            height=Theme.HEIGHT_SM,
            font=app.FONT_BUTTON,
            fg_color=Theme.BUTTON_PRIMARY_BG,
            hover_color=Theme.BUTTON_PRIMARY_HOVER,
            border_color=Theme.BUTTON_PRIMARY_BORDER,
            border_width=1,
            text_color=Theme.BUTTON_PRIMARY_TEXT,
            corner_radius=12,
            command=lambda: self.on_delete(self.task_index),
        )
        self.delete_button.grid(row=0, column=1)

    def update_text(self, new_text: str):
        self.task_text = new_text
        self.label.configure(text=new_text)


class App(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("GetItDone")
        self.geometry("800x600")

        self.FONT_TITLE = ctk.CTkFont(family=FONT_FAMILY, size=24, weight="bold")
        self.FONT_TASK = ctk.CTkFont(family=FONT_FAMILY, size=14, weight="bold")
        self.FONT_TIMESTAMP = ctk.CTkFont(family=FONT_FAMILY, size=11)
        self.FONT_BUTTON = ctk.CTkFont(family=FONT_FAMILY, size=20, weight="bold")
        self.FONT_ENTRY = ctk.CTkFont(family=FONT_FAMILY, size=18, weight="bold")

        # Set window icon
        icon_path = Path(__file__).parent / "get_it_done_logo.ico"
        if icon_path.exists():
            self.iconbitmap(str(icon_path))

        self.configure(fg_color=Theme.BG_MAIN)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.tasks = []

        self.create_layout()
        self.load_tasks()

    def _normalize_task(self, item):
        """Turn one JSON item into {"text", "created_at"}."""
        if isinstance(item, str):
            return {
                "text": item,
                "created_at": datetime.now().isoformat(),
            }

        if isinstance(item, dict) and "text" in item:
            return item

        return None

    def _format_task_date(self, task):
        try:
            when = datetime.fromisoformat(task["created_at"])
            return when.strftime("%d.%m.%Y %H:%M")
        except (KeyError, ValueError):
            return ""

    def load_tasks(self):
        ensure_tasks_file()

        try:
            with open(TASKS_FILE, encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            data = []

        if not isinstance(data, list):
            data = []

        self.tasks = []

        for item in data:
            task = self._normalize_task(item)

            if task is None:
                continue

            self.tasks.append(task)
            self._add_task_widget(
                task,
                len(self.tasks) - 1,
            )

    def save_tasks(self):
        with open(TASKS_FILE, "w", encoding="utf-8") as f:
            json.dump(
                self.tasks,
                f,
                indent=4,
                ensure_ascii=False,
            )

    def _add_task_widget(self, task, index):
        widget = TaskWidget(
            self.scrollable_frame,
            task["text"],
            self._format_task_date(task),
            index,
            on_edit=self.edit_task,
            on_delete=self.delete_task,
        )

        widget.grid(
            row=index,
            column=0,
            sticky="ew",
            pady=(0, 15),
        )

        self.task_widgets.append(widget)

    def create_layout(self):

        self.center_frame = ctk.CTkFrame(
            self,
            fg_color="transparent",
        )

        self.center_frame.grid(
            row=0,
            column=0,
        )

        self.heading = ctk.CTkLabel(
            self.center_frame,
            text="Get it done",
            font=self.FONT_TITLE,
            text_color=Theme.TEXT,
        )

        self.heading.grid(
            row=0,
            column=0,
            sticky="n",
            padx=30,
            pady=(15, 10),
        )

        self.task_card = ctk.CTkFrame(
            self.center_frame,
            width=620,
            height=440,
            fg_color=Theme.BG_CARD,
            corner_radius=Theme.RADIUS_LG,
            border_width=Theme.BORDER_WIDTH,
            border_color=Theme.BORDER,
        )

        self.task_card.grid(
            row=1,
            column=0,
            pady=(0, 15),
        )

        self.task_card.grid_propagate(False)

        self.task_card.grid_columnconfigure(0, weight=1)
        self.task_card.grid_rowconfigure(2, weight=1)

        self.create_entry()
        self.create_buttons()
        self.create_scrollable_task_list()

    def create_entry(self):

        self.task_entry = ctk.CTkEntry(
            self.task_card,
            placeholder_text="Add a task.....",
            font=self.FONT_ENTRY, 
            height=Theme.HEIGHT_MD,
            fg_color=Theme.BG_WIDGET,
            border_color=Theme.BORDER,
            border_width=Theme.BORDER_WIDTH,
            text_color=Theme.TEXT,
            placeholder_text_color=Theme.TEXT_MUTED,
            corner_radius=Theme.RADIUS_MD,
        )

        self.task_entry.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=30,
            pady=(20, 15),
        )

        def focus_in(event):
            self.task_entry.configure(
                border_color=Theme.ACCENT_HOVER
            )

        def focus_out(event):
            self.task_entry.configure(
                border_color=Theme.BORDER
            )

        self.task_entry.bind("<FocusIn>", focus_in)
        self.task_entry.bind("<FocusOut>", focus_out)
        self.task_entry.bind(
            "<Return>",
            lambda event: self.add_task(),
        )

    def create_buttons(self):

        self.button_frame = ctk.CTkFrame(
            self.task_card,
            fg_color="transparent",
        )

        self.button_frame.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=30,
            pady=(0, 15),
        )

        self.button_frame.grid_columnconfigure(
            0,
            weight=1,
        )

        self.add_button = ctk.CTkButton(
            self.button_frame,
            font=self.FONT_BUTTON,
            text="Add Task",
            command=self.add_task,
            fg_color=Theme.BUTTON_PRIMARY_BG,
            hover_color=Theme.BUTTON_PRIMARY_HOVER,
            border_color=Theme.BUTTON_PRIMARY_BORDER,
            border_width=1,
            text_color=Theme.BUTTON_PRIMARY_TEXT,
            height=Theme.HEIGHT_MD,
            corner_radius=Theme.RADIUS_BUTTONS,
        )

        self.add_button.grid(
            row=0,
            column=0,
            sticky="ew",
        )

    def create_scrollable_task_list(self):

        self.task_widgets = []

        self.scrollable_frame = ctk.CTkScrollableFrame(
            self.task_card,
            fg_color="transparent",
            label_text="",
            scrollbar_button_color=Theme.TASK_CARD_BG,
            scrollbar_button_hover_color=Theme.TASK_CARD_HOVER,
        )

        self.scrollable_frame.grid(
            row=2,
            column=0,
            sticky="nsew",
            padx=30,
            pady=(0, 20),
        )

        self.scrollable_frame.grid_columnconfigure(
            0,
            weight=1,
        )

    def add_task(self):

        text = self.task_entry.get().strip()

        if not text:
            return

        task = {
            "text": text,
            "created_at": datetime.now().isoformat(),
        }

        self.tasks.append(task)

        self._add_task_widget(
            task,
            len(self.tasks) - 1,
        )

        self.task_entry.delete(0, "end")

        self.save_tasks()

    def delete_task(self, index):

        if index < 0 or index >= len(self.tasks):
            return

        del self.tasks[index]

        self.task_widgets[index].destroy()
        del self.task_widgets[index]

        # Re-index remaining widgets
        for i, widget in enumerate(self.task_widgets):
            widget.task_index = i
            widget.grid(
                row=i,
                column=0,
                sticky="ew",
                pady=(0, 10),
            )

        self.save_tasks()

    def edit_task(self, index):

        if index < 0 or index >= len(self.tasks):
            return

        task = self.tasks[index]
        current_text = task["text"]

        dialog = ctk.CTkToplevel(self)
        dialog.title("Edit Task")
        dialog.geometry("400x200")
        dialog.configure(fg_color=Theme.BG_MAIN)

        dialog.transient(self)
        dialog.grab_set()

        dialog.grid_columnconfigure(0, weight=1)
        dialog.grid_rowconfigure(0, weight=1)

        dialog_frame = ctk.CTkFrame(
            dialog,
            fg_color=Theme.BG_CARD,
            corner_radius=Theme.RADIUS_LG,
            border_width=Theme.BORDER_WIDTH,
            border_color=Theme.BORDER,
        )

        dialog_frame.grid(
            row=0,
            column=0,
            padx=20,
            pady=20,
            sticky="nsew",
        )

        dialog_frame.grid_columnconfigure(0, weight=1)

        entry = ctk.CTkEntry(
            dialog_frame,
            font=self.FONT_ENTRY,
            height=Theme.HEIGHT_MD,
            fg_color=Theme.BG_WIDGET,
            border_color=Theme.BORDER,
            border_width=Theme.BORDER_WIDTH,
            text_color=Theme.TEXT,
            placeholder_text_color=Theme.TEXT_MUTED,
            corner_radius=Theme.RADIUS_MD,
        )

        entry.insert(0, current_text)

        entry.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=20,
            pady=(20, 10),
        )

        entry.focus()
        entry.select_range(0, "end")

        button_frame = ctk.CTkFrame(
            dialog_frame,
            fg_color="transparent",
        )

        button_frame.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=20,
            pady=(0, 20),
        )

        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)

        def save_edit():
            new_text = entry.get().strip()

            if new_text:
                task["text"] = new_text

                self.task_widgets[index].update_text(task["text"])

                self.save_tasks()

            dialog.destroy()

        def cancel_edit():
            dialog.destroy()

        save_button = ctk.CTkButton(
            button_frame,
            text="Save",
            font=self.FONT_BUTTON,
            command=save_edit,
            fg_color=Theme.BUTTON_PRIMARY_BG,
            hover_color=Theme.BUTTON_PRIMARY_HOVER,
            border_color=Theme.BUTTON_PRIMARY_BORDER,
            border_width=1,
            text_color=Theme.BUTTON_PRIMARY_TEXT,
            height=Theme.HEIGHT_MD,
            corner_radius=Theme.RADIUS_BUTTONS,
        )

        save_button.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=(0, 5),
        )

        cancel_button = ctk.CTkButton(
            button_frame,
            text="Cancel",
            font=self.FONT_BUTTON,
            command=cancel_edit,
            fg_color=Theme.BUTTON_SECONDARY_BG,
            hover_color=Theme.BUTTON_SECONDARY_HOVER,
            border_color=Theme.BUTTON_SECONDARY_BORDER,
            border_width=1,
            text_color=Theme.BUTTON_SECONDARY_TEXT,
            height=Theme.HEIGHT_MD,
            corner_radius=Theme.RADIUS_BUTTONS,
        )

        cancel_button.grid(
            row=0,
            column=1,
            sticky="ew",
            padx=(5, 0),
        )

        entry.bind(
            "<Return>",
            lambda event: save_edit(),
        )
        entry.bind(
            "<Escape>",
            lambda event: cancel_edit(),
        )


if __name__ == "__main__":
    app = App()
    app.mainloop()