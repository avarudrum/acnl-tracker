import csv
import os
import tkinter as tk
from tkinter import ttk

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

BUGS_CSV_PATH = os.path.join(BASE_DIR, "data", "bugs.csv")
FISH_CSV_PATH = os.path.join(BASE_DIR, "data", "fish.csv")

BUG_COLUMNS = ["Name", "Location", "Season", "Time", "Price", "Donated"]
FISH_COLUMNS = ["Name", "Location", "Season", "Time", "Price", "Shadow Size", "Donated"]
SHADOW_SIZES = ["Tiny", "Small", "Medium", "Large", "X-Large"]

DONATED_SYMBOLS = {"Yes": "✓", "No": "✗"} 

# Loads the CSV data into a list of dictionaries
# Used to access and edit the each museum category's data
def load_csv_data(path):
    with open(path, newline="", encoding="utf-8") as csv_file:
        return list(csv.DictReader(csv_file))

# Saves the donation status back to the CSV file
def save_donation_status(rows, path):
    with open(path, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

class FilterSpec:
    """One filter dropdown: keeps only rows whose `column` matches the selected option.

    `options` is either a fixed list (e.g. the four seasons) or a function that derives
    the list from the loaded rows (e.g. whatever locations actually appear in the data).

    `mode` is "equals" for a plain exact match, or "contains" for columns that can hold
    several comma-joined values at once (e.g. Season being "Spring, Fall").
    """

    def __init__(self, column, label, options, mode="equals", width=12):
        self.column = column
        self.label = label
        self.options = options
        self.mode = mode
        self.width = width


class CategoryWindow(tk.Toplevel):
    """Base window for browsing one museum category's CSV data.

    Subclasses set category_name, csv_path, columns, column_config, and filters;
    loading the CSV, building the table, searching, filtering, and the Donated
    double-click/save toggle are all shared here.
    """

    category_name = ""
    csv_path = None
    columns = []
    column_config = {}   # {column: (width, anchor)}
    filters = []          # list of FilterSpec, in display order

    def __init__(self, parent):
        super().__init__(parent)
        self.title(self.category_name)
        self.geometry("1500x800")

        self.rows = load_csv_data(self.csv_path)

        ttk.Label(self, text=self.category_name, font=("Segoe UI", 16, "bold")).pack(
            anchor="w", padx=10, pady=(10, 5)
        )

        self._build_filter_bar()

        # Similar to div container which holds the table and the scrollbar
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Data Table Widget type Tree view
        # Flat table that only shows the rows and columns like a file browser
        self.tree = ttk.Treeview(
            tree_frame, columns=self.columns, show="headings", selectmode="browse"
        )
        for col in self.columns:
            self.tree.heading(col, text=col)
            width, anchor = self.column_config.get(col, (120, "w"))
            self.tree.column(col, width=width, anchor=anchor)

        # Scrollbar configuration
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        # Donation column instructions for toggling the checkmark
        ttk.Label(
            self, text="Double-click the Donated cell to toggle ✓ / ✗.",
            foreground="gray"
        ).pack(anchor="w", padx=10, pady=(0, 10))

        self.tree.bind("<Double-1>", self._on_double_click)

        self._apply_filters()

    # Building the top row of controls for filtering the category
    def _build_filter_bar(self):
        # Filter bar frame; a horizontal strip
        bar = ttk.Frame(self)
        bar.pack(fill="x", padx=10, pady=(0, 5))

        # Search filter
        ttk.Label(bar, text="Search:").pack(side="left")
        self.search_var = tk.StringVar()
        ttk.Entry(bar, textvariable=self.search_var, width=18).pack(
            side="left", padx=(4, 12)
        )
        # Apply filters with each keystroke in the search box
        self.search_var.trace_add("write", lambda *_: self._apply_filters())

        # Each subclass supplies its own list of dropdown filters (can be empty)
        self.filter_vars = {}
        for spec in self.filters:
            options = spec.options(self.rows) if callable(spec.options) else spec.options

            ttk.Label(bar, text=f"{spec.label}:").pack(side="left")
            var = tk.StringVar(value="All")
            box = ttk.Combobox(
                bar, textvariable=var, values=["All"] + list(options),
                state="readonly", width=spec.width
            )
            box.pack(side="left", padx=(4, 12))
            # Applies filters when a new option is selected from the dropdown
            box.bind("<<ComboboxSelected>>", lambda *_: self._apply_filters())
            self.filter_vars[spec.column] = (var, spec.mode)

        ttk.Button(bar, text="Clear Filters", command=self._clear_filters).pack(side="left")

    def _row_matches_filters(self, row):
        for column, (var, mode) in self.filter_vars.items():
            selected = var.get()
            if selected == "All":
                continue
            if mode == "contains":
                if selected not in row[column]:
                    return False
            elif row[column] != selected:
                return False
        return True

    def _apply_filters(self):
        search = self.search_var.get().strip().lower()
        donated_index = self.columns.index("Donated")

        self.tree.delete(*self.tree.get_children())
        for row in self.rows:
            if search and search not in row["Name"].lower():
                continue
            if not self._row_matches_filters(row):
                continue
            values = [row[c] for c in self.columns]
            values[donated_index] = DONATED_SYMBOLS[row["Donated"]]
            self.tree.insert("", "end", iid=row["Name"], values=values)

    def _clear_filters(self):
        self.search_var.set("")
        for var, _mode in self.filter_vars.values():
            var.set("All")
        self._apply_filters()

    def _on_double_click(self, event):
        if self.tree.identify_region(event.x, event.y) != "cell":
            return
        row_id = self.tree.identify_row(event.y)
        col_id = self.tree.identify_column(event.x)
        if not row_id or self.columns[int(col_id[1:]) - 1] != "Donated":
            return

        # If the user double clicks the Donated cell, toggle Yes/No and save back to the CSV
        row = next(r for r in self.rows if r["Name"] == row_id)
        row["Donated"] = "No" if row["Donated"] == "Yes" else "Yes"
        save_donation_status(self.rows, self.csv_path)
        self._apply_filters()


class FishWindow(CategoryWindow):
    """Window listing every fish, sourced from data/fish.csv.

    Double click the Donated cell to toggle Yes/No which then saves it back to the CSV.
    """

    category_name = "Fish"
    csv_path = FISH_CSV_PATH
    columns = FISH_COLUMNS
    column_config = {
        "Name": (140, "w"),
        "Location": (130, "w"),
        "Season": (140, "w"),
        "Time": (110, "center"),
        "Price": (70, "e"),
        "Shadow Size": (90, "center"),
        "Donated": (80, "center"),
    }
    filters = [
        FilterSpec(
            "Location", "Location",
            lambda rows: sorted({row["Location"] for row in rows}), width=16
        ),
        FilterSpec(
            "Season", "Season",
            ["Spring", "Summer", "Fall", "Winter"], mode="contains", width=10
        ),
        FilterSpec("Shadow Size", "Shadow Size", SHADOW_SIZES, width=10),
        FilterSpec("Donated", "Donated", ["Yes", "No"], width=8),
    ]