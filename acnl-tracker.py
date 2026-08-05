import tkinter as tk
from tkinter import ttk


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
        ttk.Label(self, text="(Museum content goes here)").grid(row=1, column=0, sticky="w")


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