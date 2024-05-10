"""User interface for Flight within USA displayer"""
from tkinter import ttk, font
import tkinter as tk
from model import Observer
from search_tabs import FlightTab, AirportTab, AirlineTab
from data_storytelling_tab import DataStoryTellingTab

class UI(tk.Tk, Observer):
    """
    UI to show information about flights delay
    """
    def __init__ (self, controller) -> None:
        super().__init__()
        self.title('Flight within USA displayer')
        self.__controller = controller
        self.__tabs = {}
        self.default_font = font.nametofont('TkDefaultFont')
        self.default_font.configure(family='Times', size=12)
        self.init_components()

    @property
    def controller(self):
        """
        Getter for controller attribute
        """
        return self.__controller

    @property
    def notebook(self):
        """
        Getter for notebook attribute
        """
        return self.__notebook

    @property
    def tabs(self):
        """
        Getter for tabs attribute
        """
        return self.__tabs

    def init_components(self):
        """
        Create 5 tabs consist of
        -Search by Flight
        -Search by Airport
        -Search by Airline
        -Overall Delay Statistics
        -Exit
        """
        airport_codes = self.controller.get_airport()
        airline_codes = self.controller.get_airline()
        self.__notebook = ttk.Notebook(self)
        flight_tab = FlightTab(self, self.controller, airport_codes)
        self.__notebook.add(flight_tab, text="Search by Flight")
        self.__tabs["Search by Flight"] = [flight_tab, False]
        airport_tab = AirportTab(self, self.controller, airport_codes)
        self.__notebook.add(airport_tab, text="Search by Airport")
        self.__tabs["Search by Airport"] = [airport_tab, False]
        airline_tab = AirlineTab(self, self.controller, airline_codes)
        self.__notebook.add(airline_tab, text="Search by Airline")
        self.__tabs["Search by Airline"] = [airline_tab, False]
        data_story_telling_tab = DataStoryTellingTab(self, self.controller)
        self.__notebook.add(data_story_telling_tab, text="Overall Delay Statistics")
        self.__tabs["Overall Delay Statistics"] = [data_story_telling_tab, True]
        self.__notebook.add(tk.Frame(self), text="Exit")
        self.__tabs["Exit"] = [0, True]
        self.__notebook.pack(expand=True, fill="both")
        self.__notebook.bind('<<NotebookTabChanged>>', self.on_tab_change)

    def on_tab_change(self, event):
        """
        Event handler for notebook when current tab is changed
        """
        tab_text = event.widget.tab('current')['text']
        if tab_text == "Search by Flight":
            self.controller.set_search_type(0)
        elif tab_text == "Search by Airport":
            self.controller.set_search_type(1)
        elif tab_text == "Search by Airline":
            self.controller.set_search_type(2)
        elif tab_text == "Overall Delay Statistics":
            return
        else:
            self.destroy()
        if not self.__tabs[tab_text][1]:
            self.__tabs[tab_text][1] = True
            self.after(1,self.controller.avg_delay_flight)

    def get_cur_tab(self):
        """
        Get the current tab.
        : return : a SearchTab or DataStoryTellingTab of the selected tab
        """
        tab_text = self.notebook.tab(self.notebook.select(), "text")
        return self.__tabs[tab_text][0]

    def run(self):
        """
        Start the UI
        """
        self.mainloop()

    def update(self):
        self.controller.update_graph_stats()
