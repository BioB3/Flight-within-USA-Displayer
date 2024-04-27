"""User interface for Flight within USA displayer"""
import tkinter as tk
from tkinter import ttk
from model import Model

class UI(tk.Tk):
    def __init__ (self, model:Model) -> None:
        super().__init__()
        self.title('Flight within USA displayer')
        self.__model = model