"""User interface for Flight within USA displayer"""
from tkinter import ttk, font
from abc import ABC, abstractmethod
import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib
import matplotlib.pyplot as plt
from model import Observer
matplotlib.use("TkAgg")

class UI(tk.Tk, Observer):
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
        return self.__controller

    @property
    def notebook(self):
        return self.__notebook

    @property
    def tabs(self):
        return self.__tabs

    def init_components(self):
        airport_codes = self.controller.get_airport()
        airline_codes = self.controller.get_airline()
        self.__notebook = ttk.Notebook(self)
        flight_tab = FlightTab(self, self.controller, airport_codes)
        self.__notebook.add(flight_tab, text="Search by Flight")
        self.__tabs["Search by Flight"] = flight_tab
        airport_tab = AirportTab(self, self.controller, airport_codes)
        self.__notebook.add(airport_tab, text="Search by Airport")
        self.__tabs["Search by Airport"] = airport_tab
        airline_tab = AirlineTab(self, self.controller, airline_codes)
        self.__notebook.add(airline_tab, text="Search by Airline")
        self.__tabs["Search by Airline"] = airline_tab
        data_story_telling_tab = DataStoryTellingTab(self, self.controller)
        self.__notebook.add(data_story_telling_tab, text="Overall Delay Statistics")
        self.__notebook.add(tk.Frame(self), text="Exit")
        self.__notebook.pack(expand=True, fill="both")
        self.__notebook.bind('<<NotebookTabChanged>>', self.on_tab_change)

    def on_tab_change(self, event):
        tab = event.widget.tab('current')['text']
        if tab == "Search by Flight":
            self.controller.set_search_type(0)
        elif tab == "Search by Airport":
            self.controller.set_search_type(1)
        elif tab == "Search by Airline":
            self.controller.set_search_type(2)
        elif tab == "Overall Delay Statistics":
            return
        else:
            self.destroy()

    def get_cur_tab(self):
        tab_text = self.notebook.tab(self.notebook.select(), "text")
        return self.__tabs[tab_text]

    def run(self):
        self.mainloop()

    def update(self):
        self.controller.update_graph_stats()

class SearchTab(tk.Frame, ABC):
    def __init__(self, parent, controller, data, **kwargs) -> None:
        super().__init__(parent, **kwargs)
        self.controller = controller
        self.data = data
        self.graph : GraphFrame
        self.graph_type = ["average delay",
                           "% on-time",
                           "% time blk"]
        self.cur_graph = self.graph_type[0]
        self.init_components()

    def init_components(self):
        self.text = tk.Text(self, width=29, state="disabled")
        scroll_bar = tk.Scrollbar(self, command=self.text.yview)
        self.text.config(yscrollcommand=scroll_bar.set)
        graph_and_bt = self.create_graph_and_buttons()
        self.sort_bar = SortBar(self)
        self.sort_bar.add_label("*The line graph will not be plotted*\n"+
                                "*if all the flights are in one week*")
        self.sort_bar.add_checkboxes()
        self.text.pack(side="left", fill="y")
        scroll_bar.pack(side="left", fill="y")
        graph_and_bt.pack(side="left", fill="both",expand="True")
        self.sort_bar.pack(side="right", padx=10)

    def create_graph_and_buttons(self):
        center_frame = tk.Frame(self)
        self.graph = GraphFrame(center_frame)
        button_frame = tk.Frame(center_frame)
        avg_delay = tk.Button(button_frame, text="Average Delay",
                                   command=self.handle_avg_button)
        on_time = tk.Button(button_frame, text="% On-time Flight",
                                 command=self.handle_on_time_button)
        time_blk = tk.Button(button_frame, text="% Departure Time Block",
                             command=self.handle_time_blk_button)
        self.graph.pack(side="top", fill="both", expand=True)
        avg_delay.pack(side="left")
        on_time.pack(side="left")
        time_blk.pack(side="left")
        button_frame.pack(side="bottom")
        return center_frame

    def get_selected_filter(self):
        a_code = []
        for combo_box in self.sort_bar.cb_list:
            a_code.append(combo_box.cb_val)
        wk = self.sort_bar.checkboxes.week_var
        tb = self.sort_bar.checkboxes.time_blk_var
        return a_code, wk, tb

    def get_available_dest(self):
        selected = self.sort_bar.cb_list[0].cb_val
        return sorted(self.data[selected])

    def update_text(self, text):
        self.text["state"] = "normal"
        self.text.delete("1.0", "end")
        self.text.insert("end", text)
        self.text["state"] = "disabled"

    def update_lower_box(self, *args):
        new_load = self.get_available_dest()
        self.sort_bar.cb_list[1].update_load(new_load)

    def handle_avg_button(self):
        self.cur_graph = self.graph_type[0]
        self.after(1,self.controller.avg_delay_flight)

    def handle_on_time_button(self):
        self.cur_graph = self.graph_type[1]
        self.after(1, self.controller.percent_on_time)

    def handle_time_blk_button(self):
        self.cur_graph = self.graph_type[2]
        self.after(1,self.controller.percent_time_blk)

    @abstractmethod
    def init_sort_bar(self):
        raise NotImplementedError

class FlightTab(SearchTab):
    def __init__(self, parent, controller, data, **kwargs) -> None:
        super().__init__(parent, controller, data, **kwargs)
        self.init_sort_bar()

    def init_sort_bar(self):
        self.sort_bar.add_cb_box("Origin Airport:", sorted(self.data.keys()))
        self.sort_bar.add_cb_box("Destination Airport:", self.get_available_dest())
        self.sort_bar.cb_list[0].bind_cb(self.update_lower_box, "+")

class AirportTab(SearchTab):
    def __init__(self, parent, controller, data, **kwargs) -> None:
        super().__init__(parent, controller, data, **kwargs)
        self.init_sort_bar()

    def init_sort_bar(self):
        self.sort_bar.add_cb_box("Airport:", sorted(self.data.keys()))

class AirlineTab(SearchTab):
    def __init__(self, parent, controller, data, **kwargs) -> None:
        super().__init__(parent, controller, data, **kwargs)
        self.init_sort_bar()

    def init_sort_bar(self):
        self.sort_bar.add_cb_box("Airline ID:", self.data)

class DataStoryTellingTab(tk.Frame):
    def __init__(self, parent, controller, **kwargs) -> None:
        super().__init__(parent, **kwargs)
        self.controller = controller
        self.init_components()

    def init_components(self):
        data = self.controller.data_story_telling_data()
        descriptive_stat = tk.Text(self, width=30)
        descriptive_stat.insert("end", data[0])
        descriptive_stat["state"] = "disabled"
        scroll_bar = tk.Scrollbar(self, command=descriptive_stat.yview)
        descriptive_stat.config(yscrollcommand=scroll_bar.set)
        scroll_bar.pack(side="right", fill="y")
        descriptive_stat.pack(side="right", fill="y", expand=True)
        graph_cycle_frame = DataStoryTellingGraphFrame(self, data)
        graph_cycle_frame.pack(side="left", fill="both", expand=True)

class SortBar(tk.Frame):
    def __init__(self, parent, **kwargs) -> None:
        super().__init__(parent, **kwargs)
        self.__checkboxes: CheckBoxFrame
        self.__cb_list = []

    @property
    def cb_list(self):
        return self.__cb_list

    @property
    def checkboxes(self):
        return self.__checkboxes

    def add_cb_box(self, label: str, load: list):
        cb_frame = ComboboxFrame(self, label, load)
        self.__cb_list.append(cb_frame)
        cb_frame.pack(side="top")

    def add_checkboxes(self):
        self.__checkboxes = CheckBoxFrame(self)
        self.__checkboxes.pack(side="bottom")

    def add_label(self, text:str):
        label = tk.Label(self, text=text)
        label.pack(side="bottom")

class CheckBoxFrame(tk.Frame):
    WEEK = ["Week 1", "Week 2", "Week 3", "Week 4", "Week 5"]
    TIME_BLK = ["Early Morning", "Morning", "Afternoon", "Evening", "Night"]

    def __init__(self, parent, **kwargs) -> None:
        super().__init__(parent, **kwargs)
        self.wk_numpicks = 5
        self.time_blk_numpicks = 5
        self.__week_var = [tk.BooleanVar(value=True) for _ in range(5)]
        self.__time_blk_var = [tk.BooleanVar(value=True) for _ in range(5)]
        self.init_components()

    @property
    def week_var(self):
        week_lst = [var.get() for var in self.__week_var]
        return week_lst

    @property
    def time_blk_var(self):
        time_blk_lst = [var.get() for var in self.__time_blk_var]
        return time_blk_lst

    def init_components(self):
        week_label = tk.Label(self,text="Week of the month (min: 2):")
        week_label.pack(anchor="w")
        for _ in range(5):
            checkbox = tk.Checkbutton(self, text=self.WEEK[_],
                                      variable=self.__week_var[_],
                                      command=self.checkmin(self.__week_var[_],2,"wk"))
            checkbox.pack(anchor="w")
        time_blk_label = tk.Label(self,text="Departure time block (min: 1):")
        time_blk_label.pack(anchor="w")
        for _ in range(5):
            checkbox = tk.Checkbutton(self, text=self.TIME_BLK[_],
                                      variable=self.__time_blk_var[_],
                                      command=self.checkmin(self.__time_blk_var[_],1,"time_blk"))
            checkbox.pack(anchor="w")

    def checkmin(self, var, minpick, check_type):
        def update_num_picks():
            if not var.get():
                if check_type == "wk":
                    if self.wk_numpicks > minpick:
                        self.wk_numpicks -= 1
                    else:
                        var.set(True)
                else:
                    if self.time_blk_numpicks > minpick:
                        self.time_blk_numpicks -= 1
                    else:
                        var.set(True)
            else:
                if check_type == "wk":
                    self.wk_numpicks += 1
                else:
                    self.time_blk_numpicks += 1
        return update_num_picks

class ComboboxFrame(tk.Frame):
    def __init__(self, parent, label: str, load: list, **kwargs) -> None:
        super().__init__(parent, **kwargs)
        self.__cb_val = tk.StringVar()
        self.__label = label
        self.__load = load
        self.init_components()

    @property
    def cb_val(self):
        return self.__cb_val.get()

    def init_components(self):
        cb_box_label = tk.Label(self, text=self.__label)
        self.__cb_box = ttk.Combobox(self, textvariable=self.__cb_val, values=self.__load)
        self.__cb_box.current(newindex=0)
        cb_box_label.pack()
        self.__cb_box.pack()
        self.__cb_box.bind("<KeyRelease>", self.search)

    def bind_cb(self, func=None, add=None):
        self.__cb_box.bind("<<ComboboxSelected>>", func, add)

    def update_load(self, new_load):
        self.__load = new_load
        self.__cb_box["values"] = self.__load
        self.__cb_box.current(newindex=0)

    def search(self, event):
        inputted_val = event.widget.get()
        if not inputted_val:
            self.__cb_box["values"] = self.__load
        else:
            option = []
            for item in self.__load:
                if item.startswith(inputted_val.upper()):
                    option.append(item)
            self.__cb_box["values"] = option

class GraphFrame(tk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.canvas : FigureCanvasTkAgg
        self.init_components()

    def init_components(self):
        fig = Figure(dpi=85)
        self.canvas = FigureCanvasTkAgg(fig, self)
        toolbar = NavigationToolbar2Tk(self.canvas, self)
        toolbar.update()
        self.canvas.get_tk_widget().pack(side="top", fill="both", expand=True)

    def plot_graph(self, data, g_type):
        self.canvas.figure.clf()
        ax = self.canvas.figure.subplots()
        if g_type == "average delay":
            tick_label = [f"Week {i}" for i in data.index]
            ax.set_xlabel("Week of the Month")
            ax.set_ylabel("Average Delay Time (mins)")
            ax.set_title("Average Delays")
            ax.set_xticks(data.index, tick_label)
            ax.plot(data.index, data["DEP_DELAY"], label="Departure Delay", color="lime")
            ax.plot(data.index, data["ARR_DELAY"], label="Arrival Delay", color="red")
            ax.legend(loc="lower left", bbox_to_anchor=(0,1))
        else:
            colors = ["lime","darkorange","cyan","red","magenta"]
            pie = ax.pie(data, colors=colors, startangle=90)
            percent = 100.*data/data.sum()
            labels = ["{0} - {1:1.2f} %".format(i, j) for i, j in zip(data.index,percent)]
            if g_type == "% on-time":
                ax.set_title("Percentage of Flight departing on-time")
                ax.legend(pie[0], labels, title="Flight", loc="lower right",
                        bbox_to_anchor=(1,0), fontsize=8,
                        bbox_transform=self.canvas.figure.transFigure, ncol=2)
            else:
                ax.set_title("Percentage of Flight in each Time Block")
                ax.legend(pie[0], labels, title="Time Block", loc="lower right",
                        bbox_to_anchor=(1,0), fontsize=8,
                        bbox_transform=self.canvas.figure.transFigure, ncol=2)
        self.canvas.draw()

class DataStoryTellingGraphFrame(tk.Frame):
    def __init__(self, parent, data, **kwargs):
        super().__init__(parent, **kwargs)
        self.data = data
        self.init_components()

    def init_components(self):
        hist_frame = tk.Frame(self)
        hist_fig = Figure(dpi=85)
        histogram = FigureCanvasTkAgg(hist_fig, hist_frame)
        histogram.get_tk_widget().pack(side="top", fill="both", expand=True)
        hist_toolbar = NavigationToolbar2Tk(histogram, hist_frame)
        hist_toolbar.update()
        ax = histogram.figure.subplots()
        ax.hist(self.data[1], bins=125, alpha=0.5, label="Departure delay")
        ax.hist(self.data[2], alpha=0.5, label="Arrival delay")
        ax.legend(loc="upper right") 
        ax.set_title("Delay Time Histogram")
        ax.set_xlim(-75, 50)
        ax.set_xlabel("Delay Time (mins)")
        ax.set_ylabel("Frequency")
        histogram.draw()
        hist_frame.pack(side="top", fill="both", expand=True)
