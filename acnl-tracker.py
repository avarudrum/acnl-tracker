import csv
import os
import tkinter as tk
from tkinter import ttk

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FISH_CSV_PATH = os.path.join(BASE_DIR, "data", "fish.csv")

FISH_COLUMNS = ["Name", "Location", "Season", "Time", "Price", "Shadow Size", "Donated"]
SHADOW_SIZES = ["Tiny", "Small", "Medium", "Large", "X-Large"]
DONATED_SYMBOLS = {"Yes": "✓", "No": "✗"}  # checkmark / cross


def load_fish_data(path=FISH_CSV_PATH):
    with open(path, newline="", encoding="utf-8") as fish_data:
        return list(csv.DictReader(fish_data))


def save_fish_data(rows, path=FISH_CSV_PATH):
    with open(path, "w", newline="", encoding="utf-8") as fish_data:
        writer = csv.DictWriter(fish_data, fieldnames=FISH_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


class FishWindow(tk.Toplevel):
    """Window listing every fish, sourced from data/fish.csv.

    Double click the Donated cell to toggle Yes/No which then saves it back to the CSV.
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Fish")
        self.geometry("1500x800")

        self.rows = load_fish_data()

        ttk.Label(self, text="Fish", font=("Segoe UI", 16, "bold")).pack(
            anchor="w", padx=10, pady=(10, 5)
        )

        self._build_filter_bar()

        # Similar to div container which holds the table and the scrollbar
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Data Table Widget type Tree view 
        # flat table that only shows the rows and columns like a file browser
        self.tree = ttk.Treeview(
            tree_frame, columns=FISH_COLUMNS, show="headings", selectmode="browse"
        )

        # Filters/sections for fish viewing 
        for col in FISH_COLUMNS:
            self.tree.heading(col, text=col)
            self.tree.column("Name", width=140, anchor="w")
            self.tree.column("Location", width=130, anchor="w")
            self.tree.column("Season", width=140, anchor="w")
            self.tree.column("Time", width=110, anchor="center")
            self.tree.column("Price", width=70, anchor="e")
            self.tree.column("Shadow Size", width=90, anchor="center")
            self.tree.column("Donated", width=80, anchor="center")

        #Scrollbar configuration
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

    def _build_filter_bar(self):
        bar = ttk.Frame(self)
        bar.pack(fill="x", padx=10, pady=(0, 5))

        # Search bar for fish name
        ttk.Label(bar, text="Search:").pack(side="left")
        self.search_var = tk.StringVar()
        ttk.Entry(bar, textvariable=self.search_var, width=18).pack(
            side="left", padx=(4, 12)
        )
        self.search_var.trace_add("write", lambda *_: self._apply_filters())

        locations = ["All"] + sorted({row["Location"] for row in self.rows})
        ttk.Label(bar, text="Location:").pack(side="left")
        self.location_var = tk.StringVar(value="All")
        location_box = ttk.Combobox(
            bar, textvariable=self.location_var, values=locations,
            state="readonly", width=16
        )
        location_box.pack(side="left", padx=(4, 12))
        location_box.bind("<<ComboboxSelected>>", lambda *_: self._apply_filters())

        ttk.Label(bar, text="Season:").pack(side="left")
        self.season_var = tk.StringVar(value="All")
        season_box = ttk.Combobox(
            bar, textvariable=self.season_var,
            values=["All", "Spring", "Summer", "Fall", "Winter"],
            state="readonly", width=10
        )
        season_box.pack(side="left", padx=(4, 12))
        season_box.bind("<<ComboboxSelected>>", lambda *_: self._apply_filters())

        ttk.Label(bar, text="Shadow Size:").pack(side="left")
        self.shadow_var = tk.StringVar(value="All")
        shadow_box = ttk.Combobox(
            bar, textvariable=self.shadow_var, values=["All"] + SHADOW_SIZES,
            state="readonly", width=10
        )
        shadow_box.pack(side="left", padx=(4, 12))
        shadow_box.bind("<<ComboboxSelected>>", lambda *_: self._apply_filters())

        ttk.Label(bar, text="Donated:").pack(side="left")
        self.donated_var = tk.StringVar(value="All")
        donated_box = ttk.Combobox(
            bar, textvariable=self.donated_var, values=["All", "Yes", "No"],
            state="readonly", width=8
        )
        donated_box.pack(side="left", padx=(4, 12))
        donated_box.bind("<<ComboboxSelected>>", lambda *_: self._apply_filters())

        ttk.Button(bar, text="Clear Filters", command=self._clear_filters).pack(side="left")

    def _apply_filters(self):
        search = self.search_var.get().strip().lower()
        location = self.location_var.get()
        season = self.season_var.get()
        shadow_size = self.shadow_var.get()
        donated = self.donated_var.get()

        self.tree.delete(*self.tree.get_children())
        for row in self.rows:
            if search and search not in row["Name"].lower():
                continue
            if location != "All" and row["Location"] != location:
                continue
            if season != "All" and season not in row["Season"]:
                continue
            if shadow_size != "All" and row["Shadow Size"] != shadow_size:
                continue
            if donated != "All" and row["Donated"] != donated:
                continue
            values = [row[c] for c in FISH_COLUMNS]
            values[-1] = DONATED_SYMBOLS[row["Donated"]]
            self.tree.insert("", "end", iid=row["Name"], values=values)

    def _clear_filters(self):
        self.search_var.set("")
        self.location_var.set("All")
        self.season_var.set("All")
        self.shadow_var.set("All")
        self.donated_var.set("All")
        self._apply_filters()

    def _on_double_click(self, event):
        if self.tree.identify_region(event.x, event.y) != "cell":
            return
        row_id = self.tree.identify_row(event.y)
        col_id = self.tree.identify_column(event.x)
        if not row_id or FISH_COLUMNS[int(col_id[1:]) - 1] != "Donated":
            return

        row = next(r for r in self.rows if r["Name"] == row_id)
        row["Donated"] = "No" if row["Donated"] == "Yes" else "Yes"
        save_fish_data(self.rows)
        self._apply_filters()


class Page(ttk.Frame):
    """Base class for a tracker page: adds a consistent header label."""

    title = ""

    def __init__(self, parent):
        super().__init__(parent)
        self.columnconfigure(0, weight=1)
        ttk.Label(self, text=self.title, font=("Segoe UI", 20, "bold")).grid(
            row=0, column=0, sticky="w", pady=(0, 10)
        )
        self.build_content()

    def build_content(self):
        """Override in subclasses to add page-specific widgets, starting at row 1."""
        pass


class MayorPage(Page):
    title = "Mayor"

    def build_content(self):
        ttk.Label(self, text="(Mayor content goes here)").grid(row=1, column=0, sticky="w")


class TownPage(Page):
    title = "Town"

    def build_content(self):
        ttk.Label(self, text="Ochre", font=("Segoe UI", 14, "bold")).grid(
            row=1, column=0, sticky="w", pady=(0, 10)
        )
        ttk.Label(self, text="(Town content goes here)").grid(row=2, column=0, sticky="w")


class MuseumPage(Page):
    title = "Museum"

    def build_content(self):
        ttk.Button(self, text="Fish", command=self.open_fish_window).grid(
            row=1, column=0, sticky="w"
        )

    def open_fish_window(self):
        FishWindow(self)


class CataloguePage(Page):
    title = "Catalogue"

    def build_content(self):
        ttk.Label(self, text="(Catalogue content goes here)").grid(row=1, column=0, sticky="w")


class WishlistsPage(Page):
    title = "Wishlists"

    def build_content(self):
        ttk.Label(self, text="(Wishlists content goes here)").grid(row=1, column=0, sticky="w")


class GameNotesPage(Page):
    title = "Game Notes"

    def build_content(self):
        ttk.Label(self, text="(Game Notes content goes here)").grid(row=1, column=0, sticky="w")


class App(tk.Tk):
    PAGE_CLASSES = [
        MayorPage,
        TownPage,
        MuseumPage,
        CataloguePage,
        WishlistsPage,
        GameNotesPage,
    ]

    def __init__(self):
        super().__init__()

        self.title("Animal Crossing New Leaf Tracker")
        self.geometry("1000x650")
        self.minsize(700, 450)

        # Root grid: sidebar column is fixed, content column grows with the window
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        # Container that holds all the swappable pages
        self.pages = {}

        self._build_sidebar()
        self._build_content_area()
        self._build_pages()

        self.show_page("Mayor")

    # ---------- Sidebar ----------
    def _build_sidebar(self):
        sidebar = ttk.Frame(self, padding=10, width=180)
        sidebar.grid(row=0, column=0, sticky="ns")
        sidebar.grid_propagate(False)  # keep fixed width

        ttk.Label(sidebar, text="ACNL Tracker", font=("Segoe UI", 14, "bold")).pack(pady=(0, 20))

        for page_cls in self.PAGE_CLASSES:
            btn = ttk.Button(
                sidebar,
                text=page_cls.title,
                command=lambda s=page_cls.title: self.show_page(s)
            )
            btn.pack(fill="x", pady=4)

    # ---------- Content area ----------
    def _build_content_area(self):
        self.content = ttk.Frame(self, padding=20)
        self.content.grid(row=0, column=1, sticky="nsew")
        self.content.columnconfigure(0, weight=1)
        self.content.rowconfigure(0, weight=1)

    def _build_pages(self):
        """Instantiate one page per class, stacked on top of each other."""
        for page_cls in self.PAGE_CLASSES:
            page = page_cls(self.content)
            page.grid(row=0, column=0, sticky="nsew")  # stack pages on top of each other
            self.pages[page_cls.title] = page

    def show_page(self, name):
        """Raise the selected page to the front."""
        self.pages[name].tkraise()


if __name__ == "__main__":
    app = App()
    app.mainloop()