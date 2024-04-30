"""User interface for Flight within USA displayer"""
import tkinter as tk
import matplotlib.pyplot as plt
from tkinter import ttk
from model import FlightDataModel, Observer
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from abc import ABC, abstractmethod

class UI(tk.Tk, Observer):
    def __init__ (self, model:FlightDataModel) -> None:
        super().__init__()
        self.title('Flight within USA displayer')
        self.__model = model
        self.init_components()

    def init_components(self):
        self.init_notebook()

    def init_notebook(self):
        notebook = ttk.Notebook(self)
        notebook.add(FlightTab(self), text="Search by Flight")
        notebook.add(FlightTab(self), text="Exit")
        notebook.pack(expand=True, fill="both")
        notebook.bind('<<NotebookTabChanged>>', self.on_tab_change)
        
    def on_tab_change(self, event):
        tab = event.widget.tab('current')['text']
        if tab == 'Exit':
            self.destroy()

    def run(self):
        self.mainloop()

class SearchTab(tk.Frame,ABC):
    def __init__(self, parent, **kwargs) -> None:
        super().__init__(parent, **kwargs)

    @abstractmethod
    def init_components(self):
        pass

class FlightTab(SearchTab):
    def __init__(self, parent, **kwargs) -> None:
        super().__init__(parent, **kwargs)
        self.init_components()
        
    def init_components(self):
        self.__sort_bar = SortBar(self)
        self.__sort_bar.pack(side="right")

class SortBar(tk.Frame):
    def __init__(self, parent, **kwargs) -> None:
        super().__init__(parent, **kwargs)
        self.init_components()
    
    def init_components(self):
        self.__checkboxes = CheckBoxFrame(self)
        self.__checkboxes.pack()

class CheckBoxFrame(tk.Frame):
    WEEK = ["Week 1", "Week 2", "Week 3", "Week 4", "Week 5"]
    TIME_BLK = ["Early Morning", "Morning", "Afternoon", "Evening", "Night"]
    
    def __init__(self, parent, **kwargs) -> None:
        super().__init__(parent, **kwargs)
        self.__week_var = [tk.BooleanVar for _ in range(5)]
        self.__time_blk_var = [tk.BooleanVar for _ in range(5)]
        self.init_components()
    
    @property
    def week_var(self):
        return self.__week_var

    @property
    def time_blk_car(self):
        return self.__time_blk_var

    def init_components(self):
        for _ in range(5):
            checkbox = tk.Checkbutton(self, text=self.WEEK[_], variable=self.__week_var[_], anchor="w")
            checkbox.pack()
        for _ in range(5):
            checkbox = tk.Checkbutton(self, text=self.TIME_BLK[_], variable=self.__time_blk_var[_], anchor="w")
            checkbox.pack()        


if __name__ == "__main__":
    data_cal = FlightDataModel()
    test_ui = UI(data_cal)
    test_ui.run()
