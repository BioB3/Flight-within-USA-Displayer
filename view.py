"""User interface for Flight within USA displayer"""
from tkinter import ttk, font
from abc import ABC, abstractmethod
import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib
from model import Observer
import numpy as np
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
        tab_text = self.notebook.tab(self.notebook.select(), "text")
        return self.__tabs[tab_text][0]

    def run(self):
        self.mainloop()

    def update(self):
        self.controller.update_graph_stats()

class SearchTab(tk.Frame, ABC):
    def __init__(self, parent, controller, data, **kwargs) -> None:
        super().__init__(parent, **kwargs)
        self.controller = controller
        self.data = data
        self.graph : SearchTabGraphFrame
        self.init_components()
        self.graph_command = [self.graph.plot_avg_delay_graph,
                              self.graph.plot_on_time_graph,
                              self.graph.plot_dep_time_graph]
        self.cur_graph = self.graph_command[0]

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
        self.graph = SearchTabGraphFrame(center_frame)
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
        self.cur_graph = self.graph_command[0]
        self.after(1,self.controller.avg_delay_flight)

    def handle_on_time_button(self):
        self.cur_graph = self.graph_command[1]
        self.after(1, self.controller.percent_on_time)

    def handle_time_blk_button(self):
        self.cur_graph = self.graph_command[2]
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
        text_frame = tk.Frame(self)
        descriptive_stat = tk.Text(text_frame, width=36, wrap=tk.WORD)
        descriptive_stat.insert("end", data[0])
        descriptive_stat["state"] = "disabled"
        scroll_bar = tk.Scrollbar(text_frame, command=descriptive_stat.yview)
        descriptive_stat.config(yscrollcommand=scroll_bar.set)
        scroll_bar.pack(side="right", fill="y")
        descriptive_stat.pack(side="left", fill="y", expand=True)
        text_frame.pack(side="right", fill="y", expand=True)
        graph = DataStoryTellingGraphFrame(self, data)
        graph.pack(side="left", fill="both", expand=True)

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

class SearchTabGraphFrame(tk.Frame):
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

    def plot_avg_delay_graph(self, data):
        self.canvas.figure.clf()
        ax = self.canvas.figure.subplots()
        tick_label = [f"Week {i}" for i in data.index]
        ax.set_xlabel("Week of the Month")
        ax.set_ylabel("Average Delay Time (mins)")
        ax.set_title("Average Delays")
        ax.set_xticks(data.index, tick_label)
        ax.plot(data.index, data["DEP_DELAY"], label="Departure Delay", color="lime")
        ax.plot(data.index, data["ARR_DELAY"], label="Arrival Delay", color="red")
        ax.legend(loc="lower left", bbox_to_anchor=(0,1))
        ax.grid(axis="y")
        self.canvas.draw()

    def plot_on_time_graph(self, data):
        self.canvas.figure.clf()
        ax = self.canvas.figure.subplots()
        colors = ["lime","darkorange","cyan","red","magenta","blue"]
        pie = ax.pie(data, colors=colors, startangle=90)
        percent = 100.*data/data.sum()
        labels = ["{0} - {1:1.2f} %".format(i, j) for i, j in zip(data.index,percent)]
        ax.set_title("Percentage of Flight departing on-time")
        ax.legend(pie[0], labels, title="Flight", loc="lower right",
                bbox_to_anchor=(1,0), fontsize=8,
                bbox_transform=self.canvas.figure.transFigure, ncol=2)
        self.canvas.draw()

    def plot_dep_time_graph(self, data):
        self.canvas.figure.clf()
        ax = self.canvas.figure.subplots()
        colors = ["lime","darkorange","cyan","red","magenta"]
        pie = ax.pie(data, colors=colors, startangle=90)
        percent = 100.*data/data.sum()
        labels = ["{0} - {1:1.2f} %".format(i, j) for i, j in zip(data.index,percent)]
        ax.set_title("Percentage of Flight in each Time Block")
        ax.legend(pie[0], labels, title="Time Block", loc="lower right",
                bbox_to_anchor=(1,0), fontsize=8,
                bbox_transform=self.canvas.figure.transFigure, ncol=2)
        self.canvas.draw()

class DataStoryTellingGraphFrame(tk.Frame):
    def __init__(self, parent, data, **kwargs):
        super().__init__(parent, **kwargs)
        self.data = data
        self.canvas : FigureCanvasTkAgg
        self.toolbar : NavigationToolbar2Tk
        self.init_components()

    def init_components(self):
        fig = Figure(dpi=85)
        self.canvas = FigureCanvasTkAgg(fig, self)
        self.toolbar = NavigationToolbar2Tk(self.canvas, self)
        self.toolbar.update()
        self.plot_delay_histogram()
        buttons_frame = tk.Frame(self)
        hist_button = tk.Button(buttons_frame, text="Delays Histogram",
                                command=lambda x=1: self.after(x, self.plot_delay_histogram))
        avg_delay_button = tk.Button(buttons_frame, text="Average Delays",
                                     command=lambda x=1: self.after(x, self.plot_avg_delay))
        num_week_button = tk.Button(buttons_frame, text="Number of Flights per week",
                                    command=lambda x=1: self.after(x, self.plot_flight_week))
        num_time_button = tk.Button(buttons_frame, text="Number of Flights per time block",
                                    command=lambda x=1: self.after(x, self.plot_flight_time_blk))
        hist_button.pack(side="left")
        avg_delay_button.pack(side="left")
        num_week_button.pack(side="left")
        num_time_button.pack(side="left")
        buttons_frame.pack(side="bottom")
        self.canvas.get_tk_widget().pack(side="top", fill="both", expand=True)

    def plot_delay_histogram(self):
        self.canvas.figure.clf()
        ax = self.canvas.figure.subplots()
        ax.hist(self.data[1], bins=125, alpha=0.5, label="Departure delay")
        ax.hist(self.data[2], alpha=0.5, label="Arrival delay")
        ax.legend(loc="upper right")
        ax.set_title("Delays Time Histogram")
        ax.set_xlim(-75, 75)
        ax.set_xlabel("Delay Time (mins)")
        ax.set_ylabel("Frequency")
        self.canvas.draw()

    def plot_avg_delay(self):
        self.canvas.figure.clf()
        ax = self.canvas.figure.subplots()
        ax.set_xlabel("Day of the Month")
        ax.set_ylabel("Average Delay Time (mins)")
        ax.set_title("Average Flight Delays Time in January 2020")
        ax.set_xticks(self.data[3].index[::2])
        ax.plot(self.data[3].index, self.data[3]["DEP_DELAY"],
                label="Departure Delay", color="lime")
        ax.plot(self.data[3].index, self.data[3]["ARR_DELAY"],
                label="Arrival Delay", color="red")
        ax.legend(loc="lower left", bbox_to_anchor=(-0.15,1))
        ax.grid()
        self.canvas.draw()

    def plot_flight_week(self):
        self.canvas.figure.clf()
        ax = self.canvas.figure.subplots()
        colors = ["lime","darkorange","cyan","red","magenta","blue"]
        week = self.data[4].index
        flight_type = self.data[4].columns
        bottom = np.zeros(len(week))
        for i in range(len(flight_type)):
            ax.bar(week, self.data[4][flight_type[i]], label=flight_type[i],
                    color=colors[i], bottom=bottom)
            bottom += self.data[4][flight_type[i]]
        ax.set_ylim(0,170000)
        ax.legend(loc='upper right', ncols=3)
        ax.set_xlabel('Week of the month')
        ax.set_ylabel('Number of Flights')
        ax.set_title('Flights per week in January 2020')
        self.canvas.draw()

    def plot_flight_time_blk(self):
        self.canvas.figure.clf()
        ax = self.canvas.figure.subplots()
        colors = ["lime","darkorange","cyan","red","magenta","blue"]
        time_blk = self.data[5].index
        flight_type = self.data[5].columns
        bottom = np.zeros(len(time_blk))
        for i in range(len(flight_type)):
            ax.bar(time_blk, self.data[5][flight_type[i]], label=flight_type[i],
                    color=colors[i], bottom=bottom)
            bottom += self.data[5][flight_type[i]]
        ax.set_ylim(0,175000)
        ax.legend(loc='upper right', ncols=3)
        ax.set_xlabel('Departure Time Block')
        ax.set_ylabel('Number of Flights')
        ax.set_title('Flights per time block in January 2020')
        self.canvas.draw()
