"""Frames for data exploration tabs of Flight within USA displayer"""
import tkinter as tk
from tkinter import ttk
from abc import ABC, abstractmethod
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib
matplotlib.use("TkAgg")

class SearchTab(tk.Frame, ABC):
    """
    Abstract Frame for user to select subsets of data to view information.
    """
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
        """
        Create a graph frame, text, scrollbar to show statistics and a sortbar
        for user to select subsets of data.
        """
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
        """
        Create a frame widget consisted of a graph figure and 3 buttons
        to plot average delay graph, percentage of on-time flight graph
        and percentage of flight departed in each time block graph.
        : return : a frame widget with figure and buttons
        """
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
        """
        Get the value of combobox(es) and checkboxes selected by user
        : return : a tuple consisted of lists of selected filter
        """
        a_code = []
        for combo_box in self.sort_bar.cb_list:
            a_code.append(combo_box.cb_val)
        wk = self.sort_bar.checkboxes.week_var
        tb = self.sort_bar.checkboxes.time_blk_var
        return a_code, wk, tb

    def get_available_dest(self):
        """
        Get available destination airports list based on the orgin airport selected
        : return : a list of airports
        """
        selected = self.sort_bar.cb_list[0].cb_val
        return sorted(self.data[selected])

    def update_text(self, text):
        """
        Update the Text widget
        """
        self.text["state"] = "normal"
        self.text.delete("1.0", "end")
        self.text.insert("end", text)
        self.text["state"] = "disabled"

    def update_lower_box(self, *args):
        """
        Update the choices available of the destination airport combobox
        """
        new_load = self.get_available_dest()
        self.sort_bar.cb_list[1].update_load(new_load)

    def handle_avg_button(self):
        """
        Event handler for Average Delay Button.
        """
        self.cur_graph = self.graph_command[0]
        self.after(1,self.controller.avg_delay_flight)

    def handle_on_time_button(self):
        """
        Event handler for % On-time Flight Button
        """
        self.cur_graph = self.graph_command[1]
        self.after(1, self.controller.percent_on_time)

    def handle_time_blk_button(self):
        """
        Event handler for % Departure Time Block
        """
        self.cur_graph = self.graph_command[2]
        self.after(1,self.controller.percent_time_blk)

    @abstractmethod
    def init_sort_bar(self):
        """
        Abstract method to create a sortbar for user to select subsets of data
        """
        raise NotImplementedError

class FlightTab(SearchTab):
    """
    A tab for user to sort data using flight.
    """
    def __init__(self, parent, controller, data, **kwargs) -> None:
        super().__init__(parent, controller, data, **kwargs)
        self.init_sort_bar()

    def init_sort_bar(self):
        """
        Create 2 comboboxes for origin airport and destination airport
        """
        self.sort_bar.add_cb_box("Origin Airport:", sorted(self.data.keys()))
        self.sort_bar.add_cb_box("Destination Airport:", self.get_available_dest())
        self.sort_bar.cb_list[0].bind_cb(self.update_lower_box, "+")

class AirportTab(SearchTab):
    """
    A tab for user to sort data using airport code
    """
    def __init__(self, parent, controller, data, **kwargs) -> None:
        super().__init__(parent, controller, data, **kwargs)
        self.init_sort_bar()

    def init_sort_bar(self):
        """
        Create a combobox for airport code
        """
        self.sort_bar.add_cb_box("Airport:", sorted(self.data.keys()))

class AirlineTab(SearchTab):
    def __init__(self, parent, controller, data, **kwargs) -> None:
        super().__init__(parent, controller, data, **kwargs)
        self.init_sort_bar()

    def init_sort_bar(self):
        """
        Create a combobox for airline id
        """
        self.sort_bar.add_cb_box("Airline ID:", self.data)

class SortBar(tk.Frame):
    """
    A sort bar frame for user to select subsets of data
    """
    def __init__(self, parent, **kwargs) -> None:
        super().__init__(parent, **kwargs)
        self.__checkboxes: CheckBoxFrame
        self.__cb_list = []

    @property
    def cb_list(self):
        """
        Getter for cb_list attribute
        """
        return self.__cb_list

    @property
    def checkboxes(self):
        """
        Getter for checkboxes attribute
        """
        return self.__checkboxes

    def add_cb_box(self, label: str, load: list):
        """
        Add a combobox to the frame
        : param label : the text to be setted as label above the combobox
        : param load : the values of the combobox
        """
        cb_frame = ComboboxFrame(self, label, load)
        self.__cb_list.append(cb_frame)
        cb_frame.pack(side="top")

    def add_checkboxes(self):
        """
        Add a checkbox frame
        """
        self.__checkboxes = CheckBoxFrame(self)
        self.__checkboxes.pack(side="bottom")

    def add_label(self, text:str):
        """
        Add a label widget
        """
        label = tk.Label(self, text=text)
        label.pack(side="bottom")

class CheckBoxFrame(tk.Frame):
    """
    A frame consisted of checkboxes for user to select subsets of data
    """
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
        """
        Get the value of the week checkboxes
        """
        week_lst = [var.get() for var in self.__week_var]
        return week_lst

    @property
    def time_blk_var(self):
        """
        Get the value of the time block checkboxes
        """
        time_blk_lst = [var.get() for var in self.__time_blk_var]
        return time_blk_lst

    def init_components(self):
        """
        Create 2 sets of comboboxes, week of the month and departure time block
        """
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
        """
        Create a function to check whether the amount of checkboxes checked is lower
        than the minimum setted.
        : param var : BooleanVar object that stored that value of checkbox
        : param minpick : the minimum number of checkboxes selected
        : param check_type : the type of checkboxes to be checked
        : return : a function that prevent unchecking checkboxes if the amount of checkboxes
                   checked is lower than the minimum setted.
        """
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
    """
    A frame consisted of a label indicating the values of the combobox
    and a combobox
    """
    def __init__(self, parent, label: str, load: list, **kwargs) -> None:
        super().__init__(parent, **kwargs)
        self.__cb_val = tk.StringVar()
        self.__label = label
        self.__load = load
        self.init_components()

    @property
    def cb_val(self):
        """
        Get the selected value of the combobox
        """
        return self.__cb_val.get()

    def init_components(self):
        """
        Create a label and a combobox with values recieved when initiated.
        """
        cb_box_label = tk.Label(self, text=self.__label)
        self.__cb_box = ttk.Combobox(self, textvariable=self.__cb_val, values=self.__load)
        self.__cb_box.current(newindex=0)
        cb_box_label.pack()
        self.__cb_box.pack()
        self.__cb_box.bind("<KeyRelease>", self.search)

    def bind_cb(self, func=None, add=None):
        """
        Bind an event to the combobox
        : param func : a function to be called
        : param add : choice to preserve the old callback
        """
        self.__cb_box.bind("<<ComboboxSelected>>", func, add)

    def update_load(self, new_load):
        """
        Update the values of the combobox
        : param new_load : a list of values to add to combobox
        """
        self.__load = new_load
        self.__cb_box["values"] = self.__load
        self.__cb_box.current(newindex=0)

    def search(self, event):
        """
        An event to search for values in combobox that start with the inputted letters
        """
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
    """A frame that show graphs for Search tabs"""
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.canvas : FigureCanvasTkAgg
        self.init_components()

    def init_components(self):
        """
        Create a figure, a canvas, and a toolbar
        """
        fig = Figure(dpi=85)
        self.canvas = FigureCanvasTkAgg(fig, self)
        toolbar = NavigationToolbar2Tk(self.canvas, self)
        toolbar.update()
        self.canvas.get_tk_widget().pack(side="top", fill="both", expand=True)

    def plot_avg_delay_graph(self, data):
        """
        Plot Average Delay Line Graph based on the data recieved
        : param data : data to be used to plot graph
        """
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
        """
        Plot Percentage of on-time flights Graph based on the data recieved
        : param data : data to be used to plot graph
        """
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
        """
        Plot Percentage of flight in each time block Graph based on the data recieved
        : param data : data to be used to plot graph
        """
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
