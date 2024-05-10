"""Frame to show Data Storytelling result tab of Flight within USA displayer"""
import tkinter as tk
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib
matplotlib.use("TkAgg")

class DataStoryTellingTab(tk.Frame):
    """
    A frame that display setted graphs and desciptive statistics.
    """
    def __init__(self, parent, controller, **kwargs) -> None:
        super().__init__(parent, **kwargs)
        self.controller = controller
        self.init_components()

    def init_components(self):
        """
        Create a DataStoryTellingGraphFrame and a frame consisted of Text and
        Scrollbar widget.
        """
        data = self.controller.data_story_telling_data()
        text_frame = tk.Frame(self)
        descriptive_stat = tk.Text(text_frame, width=36, wrap=tk.WORD)
        descriptive_stat.insert("end", data[0])
        descriptive_stat["state"] = "disabled"
        scroll_bar = tk.Scrollbar(text_frame, command=descriptive_stat.yview)
        descriptive_stat.config(yscrollcommand=scroll_bar.set)
        scroll_bar.pack(side="right", fill="y")
        descriptive_stat.pack(side="left", fill="y", expand=True)
        text_frame.pack(side="right", fill="y")
        graph = DataStoryTellingGraphFrame(self, data)
        graph.pack(side="left", fill="both", expand=True)

class DataStoryTellingGraphFrame(tk.Frame):
    """
    A Frame that can show 4 graphs.
    -Delays Time Histogram
    -Average Delays Time Line graph (timeseries)
    -Number of flight per week Stacked bar graph
    -Number of flight per departure time block Stack Bar graph
    """
    def __init__(self, parent, data, **kwargs):
        super().__init__(parent, **kwargs)
        self.data = data
        self.canvas : FigureCanvasTkAgg
        self.toolbar : NavigationToolbar2Tk
        self.init_components()

    def init_components(self):
        """
        Create a Figure object, a toolbar to interact with the Figure and buttons
        to plot graphs
        """
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
        """
        Plot Delays Time Histogram
        """
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
        """
        Plot Average Delays Time Line graph
        """
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
        """
        Plot Number of flight per week Stacked bar graph
        """
        self.canvas.figure.clf()
        ax = self.canvas.figure.subplots()
        colors = ["lime","darkorange","cyan","red","magenta","blue"]
        week = self.data[4].index
        flight_type = self.data[4].columns
        bottom = np.zeros(len(week))
        for i in enumerate(flight_type):
            ax.bar(week, self.data[4][flight_type[i[0]]], label=flight_type[i[0]],
                    color=colors[i[0]], bottom=bottom)
            bottom += self.data[4][flight_type[i[0]]]
        ax.set_ylim(0,170000)
        ax.legend(loc='upper right', ncols=3)
        ax.set_xlabel('Week of the month')
        ax.set_ylabel('Number of Flights')
        ax.set_title('Flights per week in January 2020')
        self.canvas.draw()

    def plot_flight_time_blk(self):
        """
        Plot Number of flight per departure time block Stack Bar graph
        """
        self.canvas.figure.clf()
        ax = self.canvas.figure.subplots()
        colors = ["lime","darkorange","cyan","red","magenta","blue"]
        time_blk = self.data[5].index
        flight_type = self.data[5].columns
        bottom = np.zeros(len(time_blk))
        for i in enumerate(flight_type):
            ax.bar(time_blk, self.data[5][flight_type[i[0]]], label=flight_type[i[0]],
                    color=colors[i[0]], bottom=bottom)
            bottom += self.data[5][flight_type[i[0]]]
        ax.set_ylim(0,175000)
        ax.legend(loc='upper right', ncols=3)
        ax.set_xlabel('Departure Time Block')
        ax.set_ylabel('Number of Flights')
        ax.set_title('Flights per time block in January 2020')
        self.canvas.draw()
