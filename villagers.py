import os
import tkinter as tk
from tkinter import ttk

from csv_utils import load_csv_data, save_csv_rows

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

VILLAGERS_CSV_PATH = os.path.join(BASE_DIR, "data", "villagers.csv")
CURRENT_VILLAGERS_PATH = os.path.join(BASE_DIR, "data", "current_villagers.csv")
DREAMIES_PATH = os.path.join(BASE_DIR, "data", "dreamies.csv")

MASTER_COLUMNS = [
    "Name", "Species", "Personality", "Birthday",
    "Favorite Color", "Coffee Order", "Style Notes",
]
PERSONALITIES = ["Lazy", "Jock", "Cranky", "Snooty", "Normal", "Peppy", "Smug", "Sisterly"]
KEEP_SYMBOLS = {"Yes": "♥", "No": "♡"}

COLUMN_WIDTHS = {
    "Name": 120, "Species": 90, "Personality": 90, "Birthday": 90,
    "Favorite Color": 110, "Coffee Order": 160, "Style Notes": 140, "Keep": 60,
}


def load_master_villagers():
    return {row["Name"]: row for row in load_csv_data(VILLAGERS_CSV_PATH)}


def load_name_list(path):
    """Load a simple {Name, ...} CSV -- current villagers or dreamies -- as a list of dicts."""
    if not os.path.exists(path):
        return []
    return load_csv_data(path)


class VillagerTableWindow(tk.Toplevel):
    """Base window for browsing a set of villagers with search + Personality/Species filters.

    Subclasses provide _load_rows() (which villagers to show) and _build_action_bar()
    (whatever row actions make sense for that list); everything else is shared.
    """

    window_title = ""
    extra_columns = []  # appended after MASTER_COLUMNS, e.g. ["Keep"] for Current Villagers

    def __init__(self, parent):
        super().__init__(parent)
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.title(self.window_title)
        self.geometry("1500x800")

        self.villager_lookup = load_master_villagers()
        self.columns = MASTER_COLUMNS + self.extra_columns
        self.rows = self._load_rows()

        ttk.Label(self, text=self.window_title, font=("Segoe UI", 16, "bold")).pack(
            anchor="w", padx=10, pady=(10, 5)
        )

        self._build_filter_bar()

        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.tree = ttk.Treeview(
            tree_frame, columns=self.columns, show="headings", selectmode="browse"
        )
        for col in self.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=COLUMN_WIDTHS.get(col, 100), anchor="w")

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        self.status_label = ttk.Label(self, text="", foreground="gray")
        self.status_label.pack(anchor="w", padx=10, pady=(0, 5))

        self._build_action_bar()

        self.tree.bind("<Double-1>", self._on_double_click)

        self._apply_filters()

    # ---- subclass hooks ----
    def _load_rows(self):
        """Return the list of row dicts to display. Override in subclasses."""
        raise NotImplementedError

    def _build_action_bar(self):
        """Override in subclasses to add row-action buttons below the table."""
        pass

    def _on_double_click(self, event):
        """Override in subclasses that need a toggleable column (e.g. Keep)."""
        pass

    def _display_value(self, row, column):
        """Override to customize how a cell is rendered (e.g. Keep as a heart symbol)."""
        return row.get(column, "")

    # ---- shared behaviour ----
    def _selected_name(self):
        selection = self.tree.selection()
        if not selection:
            self.status_label.config(text="Select a villager first.")
            return None
        return selection[0]

    def _build_filter_bar(self):
        bar = ttk.Frame(self)
        bar.pack(fill="x", padx=10, pady=(0, 5))

        ttk.Label(bar, text="Search:").pack(side="left")
        self.search_var = tk.StringVar()
        ttk.Entry(bar, textvariable=self.search_var, width=18).pack(side="left", padx=(4, 12))
        self.search_var.trace_add("write", lambda *_: self._apply_filters())

        ttk.Label(bar, text="Personality:").pack(side="left")
        self.personality_var = tk.StringVar(value="All")
        personality_box = ttk.Combobox(
            bar, textvariable=self.personality_var, values=["All"] + PERSONALITIES,
            state="readonly", width=10
        )
        personality_box.pack(side="left", padx=(4, 12))
        personality_box.bind("<<ComboboxSelected>>", lambda *_: self._apply_filters())

        species = ["All"] + sorted({row["Species"] for row in self.rows if row["Species"]})
        ttk.Label(bar, text="Species:").pack(side="left")
        self.species_var = tk.StringVar(value="All")
        species_box = ttk.Combobox(
            bar, textvariable=self.species_var, values=species, state="readonly", width=12
        )
        species_box.pack(side="left", padx=(4, 12))
        species_box.bind("<<ComboboxSelected>>", lambda *_: self._apply_filters())

        ttk.Button(bar, text="Clear Filters", command=self._clear_filters).pack(side="left")

    def _clear_filters(self):
        self.search_var.set("")
        self.personality_var.set("All")
        self.species_var.set("All")
        self._apply_filters()

    def _apply_filters(self):
        search = self.search_var.get().strip().lower()
        personality = self.personality_var.get()
        species = self.species_var.get()

        self.tree.delete(*self.tree.get_children())
        for row in self.rows:
            if search and search not in row["Name"].lower():
                continue
            if personality != "All" and row["Personality"] != personality:
                continue
            if species != "All" and row["Species"] != species:
                continue
            values = [self._display_value(row, col) for col in self.columns]
            self.tree.insert("", "end", iid=row["Name"], values=values)

    def refresh(self):
        self.rows = self._load_rows()
        self._apply_filters()


class AllVillagersWindow(VillagerTableWindow):
    """Reference list of every villager. Lets you add one to Dreamies or move them in directly."""

    window_title = "All Villagers"

    def _load_rows(self):
        return list(self.villager_lookup.values())

    def _build_action_bar(self):
        bar = ttk.Frame(self)
        bar.pack(fill="x", padx=10, pady=(0, 10))
        ttk.Button(bar, text="Add to Dreamies", command=self._add_to_dreamies).pack(
            side="left", padx=(0, 6)
        )
        ttk.Button(bar, text="Move In", command=self._move_in).pack(side="left")

    def _add_to_dreamies(self):
        name = self._selected_name()
        if not name:
            return
        if any(row["Name"] == name for row in load_name_list(CURRENT_VILLAGERS_PATH)):
            self.status_label.config(text=f"{name} is already one of your current villagers.")
            return
        dreamies = load_name_list(DREAMIES_PATH)
        if any(row["Name"] == name for row in dreamies):
            self.status_label.config(text=f"{name} is already on your Dreamies list.")
            return
        dreamies.append({"Name": name})
        save_csv_rows(dreamies, ["Name"], DREAMIES_PATH)
        self.status_label.config(text=f"Added {name} to Dreamies.")

    def _move_in(self):
        name = self._selected_name()
        if not name:
            return
        current = load_name_list(CURRENT_VILLAGERS_PATH)
        if any(row["Name"] == name for row in current):
            self.status_label.config(text=f"{name} is already one of your current villagers.")
            return
        current.append({"Name": name, "Keep": "Yes"})
        save_csv_rows(current, ["Name", "Keep"], CURRENT_VILLAGERS_PATH)

        dreamies = [row for row in load_name_list(DREAMIES_PATH) if row["Name"] != name]
        save_csv_rows(dreamies, ["Name"], DREAMIES_PATH)

        self.status_label.config(text=f"Moved {name} into your town.")


class DreamiesWindow(VillagerTableWindow):
    """Your villager wishlist. Lets you move a dreamie in, or drop them from the list."""

    window_title = "Dreamies"

    def _load_rows(self):
        names = [row["Name"] for row in load_name_list(DREAMIES_PATH)]
        return [self.villager_lookup[name] for name in names if name in self.villager_lookup]

    def _build_action_bar(self):
        bar = ttk.Frame(self)
        bar.pack(fill="x", padx=10, pady=(0, 10))
        ttk.Button(bar, text="Move In", command=self._move_in).pack(side="left", padx=(0, 6))
        ttk.Button(bar, text="Remove from Dreamies", command=self._remove).pack(side="left")

    def _move_in(self):
        name = self._selected_name()
        if not name:
            return
        current = load_name_list(CURRENT_VILLAGERS_PATH)
        if any(row["Name"] == name for row in current):
            self.status_label.config(text=f"{name} is already one of your current villagers.")
        else:
            current.append({"Name": name, "Keep": "Yes"})
            save_csv_rows(current, ["Name", "Keep"], CURRENT_VILLAGERS_PATH)
            self.status_label.config(text=f"Moved {name} into your town.")

        dreamies = [row for row in load_name_list(DREAMIES_PATH) if row["Name"] != name]
        save_csv_rows(dreamies, ["Name"], DREAMIES_PATH)
        self.refresh()

    def _remove(self):
        name = self._selected_name()
        if not name:
            return
        dreamies = [row for row in load_name_list(DREAMIES_PATH) if row["Name"] != name]
        save_csv_rows(dreamies, ["Name"], DREAMIES_PATH)
        self.status_label.config(text=f"Removed {name} from Dreamies.")
        self.refresh()


class CurrentVillagersWindow(VillagerTableWindow):
    """Your town's residents. Double-click Keep to mark 'want to stay'; remove them if they move away."""

    window_title = "Current Villagers"
    extra_columns = ["Keep"]

    def _load_rows(self):
        rows = []
        for entry in load_name_list(CURRENT_VILLAGERS_PATH):
            name = entry["Name"]
            if name in self.villager_lookup:
                row = dict(self.villager_lookup[name])
                row["Keep"] = entry.get("Keep", "No")
                rows.append(row)
        return rows

    def _display_value(self, row, column):
        if column == "Keep":
            return KEEP_SYMBOLS.get(row.get("Keep", "No"), "♡")
        return super()._display_value(row, column)

    def _build_action_bar(self):
        bar = ttk.Frame(self)
        bar.pack(fill="x", padx=10, pady=(0, 5))
        ttk.Button(bar, text="Remove (Moved Away)", command=self._remove).pack(side="left")

        ttk.Label(
            self, text="Double-click the Keep cell to toggle ♥ / ♡.",
            foreground="gray"
        ).pack(anchor="w", padx=10, pady=(0, 10))

    def _on_double_click(self, event):
        if self.tree.identify_region(event.x, event.y) != "cell":
            return
        row_id = self.tree.identify_row(event.y)
        col_id = self.tree.identify_column(event.x)
        if not row_id or self.columns[int(col_id[1:]) - 1] != "Keep":
            return

        row = next(r for r in self.rows if r["Name"] == row_id)
        row["Keep"] = "No" if row["Keep"] == "Yes" else "Yes"
        save_csv_rows(
            [{"Name": r["Name"], "Keep": r["Keep"]} for r in self.rows],
            ["Name", "Keep"], CURRENT_VILLAGERS_PATH
        )
        self._apply_filters()

    def _remove(self):
        name = self._selected_name()
        if not name:
            return
        remaining = [row for row in load_name_list(CURRENT_VILLAGERS_PATH) if row["Name"] != name]
        save_csv_rows(remaining, ["Name", "Keep"], CURRENT_VILLAGERS_PATH)
        self.status_label.config(text=f"Removed {name} (moved away).")
        self.refresh()
