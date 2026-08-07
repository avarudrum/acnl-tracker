import json
import os
import tkinter as tk
from tkinter import ttk

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

HAIR_COLOUR_IMAGE_PATH = os.path.join(BASE_DIR, "resources", "haircolour_codes.png")
HAIRSTYLE_IMAGE_PATH = os.path.join(BASE_DIR, "resources", "hairstyle_codes.png")
HOME_LOAN_PATH = os.path.join(BASE_DIR, "data", "home_loan.json")

LOAN_PRESETS = [10_000, 50_000, 100_000, 200_000]


class ImageWindow(tk.Toplevel):

    def __init__(self, parent, title, image_path):
        super().__init__(parent)
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.title(title)

        # Kept as an attribute so Tkinter doesn't garbage-collect it and blank the label
        self.photo = tk.PhotoImage(file=image_path)
        ttk.Label(self, image=self.photo).pack(padx=10, pady=10)


def load_home_loan(path=HOME_LOAN_PATH):
    if not os.path.exists(path):
        return {"loan_total": 0, "paid": 0}
    with open(path, encoding="utf-8") as json_file:
        return json.load(json_file)


def save_home_loan(loan, path=HOME_LOAN_PATH):
    with open(path, "w", encoding="utf-8") as json_file:
        json.dump(loan, json_file)


class HomeLoanSection(ttk.Frame):
    """Shows progress toward paying off the home loan, with a button to update it."""

    def __init__(self, parent):
        super().__init__(parent)
        self.loan = load_home_loan()

        ttk.Label(self, text="Home Loan", font=("Segoe UI", 14, "bold")).grid(
            row=0, column=0, sticky="w", pady=(0, 5)
        )

        self.progress = ttk.Progressbar(self, length=300)
        self.progress.grid(row=1, column=0, sticky="w", pady=(0, 5))

        self.status_label = ttk.Label(self, text="")
        self.status_label.grid(row=2, column=0, sticky="w", pady=(0, 10))

        ttk.Button(self, text="Set Home Loan Total", command=self._open_dialog).grid(
            row=3, column=0, sticky="w"
        )

        self._refresh()

    def _open_dialog(self):
        HomeLoanDialog(self, self)

    def _refresh(self):
        total = self.loan["loan_total"]
        paid = self.loan["paid"]
        self.progress["maximum"] = max(total, 1)
        self.progress["value"] = paid
        percent = (paid / total * 100) if total else 0
        self.status_label.config(text=f"{paid:,} / {total:,} bells paid ({percent:.1f}%)")


class HomeLoanDialog(tk.Toplevel):
    """Pop-up for updating the loan: set the total, and/or add to the paid amount
    (via a preset button or by typing a custom amount) -- nothing is saved until
    the Save button is pressed.
    """

    def __init__(self, parent, section):
        super().__init__(parent)
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.title("Set Home Loan Total")
        self.section = section

        ttk.Label(self, text="Loan Total (bells):").grid(
            row=0, column=0, sticky="w", padx=10, pady=(10, 5)
        )
        self.total_var = tk.StringVar(value=str(section.loan["loan_total"]))
        ttk.Entry(self, textvariable=self.total_var, width=15).grid(
            row=0, column=1, padx=10, pady=(10, 5)
        )

        ttk.Label(self, text="Add to Paid (bells):").grid(
            row=1, column=0, sticky="w", padx=10, pady=5
        )
        self.add_var = tk.StringVar(value="0")
        ttk.Entry(self, textvariable=self.add_var, width=15).grid(
            row=1, column=1, padx=10, pady=5
        )

        preset_row = ttk.Frame(self)
        preset_row.grid(row=2, column=0, columnspan=2, sticky="w", padx=10, pady=(0, 5))
        for amount in LOAN_PRESETS:
            ttk.Button(
                preset_row, text=f"+{amount:,}",
                command=lambda amount=amount: self.add_var.set(str(amount))
            ).pack(side="left", padx=(0, 6))

        self.error_label = ttk.Label(self, text="", foreground="red")
        self.error_label.grid(row=3, column=0, columnspan=2, sticky="w", padx=10)

        ttk.Button(self, text="Save", command=self._save).grid(
            row=4, column=0, columnspan=2, pady=10
        )

    def _save(self):
        try:
            total = int(self.total_var.get())
            add_amount = int(self.add_var.get())
        except ValueError:
            self.error_label.config(text="Loan Total and Add to Paid must be whole numbers.")
            return

        loan = self.section.loan
        loan["loan_total"] = total
        loan["paid"] = min(loan["paid"] + add_amount, total)
        save_home_loan(loan)
        self.section._refresh()
        self.destroy()
