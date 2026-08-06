import os
import tkinter as tk
from tkinter import ttk

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

HAIR_COLOUR_IMAGE_PATH = os.path.join(BASE_DIR, "resources", "haircolour_codes.png")
HAIRSTYLE_IMAGE_PATH = os.path.join(BASE_DIR, "resources", "hairstyle_codes.png")


class ImageWindow(tk.Toplevel):

    def __init__(self, parent, title, image_path):
        super().__init__(parent)
        self.title(title)

        # Kept as an attribute so Tkinter doesn't garbage-collect it and blank the label
        self.photo = tk.PhotoImage(file=image_path)
        ttk.Label(self, image=self.photo).pack(padx=10, pady=10)
