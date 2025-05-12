import csv
import tkinter as tk
from tkinter import filedialog

class Reader():
    def __init__(self):
        root = tk.Tk()
        root.withdraw()
        self.path = filedialog.askopenfilenames()

    def open_explorer(self):
        return self.path

    def get_file_data(self):
        daten = []
        with open(self.path, "r", encoding= "utf-8", newline = '') as f:
            reader = csv.reader(f, delimiter = ";", quotechar = '"')
            header = next(reader)
            for line in reader:
                daten.append(line)
        return daten