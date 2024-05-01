"""User interface for Flight within USA displayer"""
from tkinter import ttk, font
from model import FlightDataModel, Observer
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from abc import ABC, abstractmethod
import tkinter as tk
import seaborn as sns
import matplotlib
matplotlib.use("TkAgg")

AIRPORTS = ['ABE', 'ABI', 'ABQ', 'ABR', 'ABY', 'ACT', 'ACV', 'ACY', 'ADK',
            'ADQ', 'AEX', 'AGS', 'ALB', 'ALO', 'AMA', 'ANC', 'APN', 'ASE',
            'ATL', 'ATW', 'ATY', 'AUS', 'AVL', 'AVP', 'AZA', 'AZO', 'BDL',
            'BET', 'BFF', 'BFL', 'BFM', 'BGM', 'BGR', 'BHM', 'BIL', 'BIS',
            'BJI', 'BLI', 'BLV', 'BMI', 'BNA', 'BOI', 'BOS', 'BPT', 'BQK',
            'BQN', 'BRD', 'BRO', 'BRW', 'BTM', 'BTR', 'BTV', 'BUF', 'BUR',
            'BWI', 'BZN', 'CAE', 'CAK', 'CDC', 'CDV', 'CGI', 'CHA', 'CHO',
            'CHS', 'CID', 'CIU', 'CKB', 'CLE', 'CLL', 'CLT', 'CMH', 'CMI',
            'CMX', 'CNY', 'COD', 'COS', 'COU', 'CPR', 'CRP', 'CRW', 'CSG',
            'CVG', 'CWA', 'CYS', 'DAB', 'DAL', 'DAY', 'DBQ', 'DCA', 'DEN',
            'DFW', 'DHN', 'DLH', 'DRO', 'DRT', 'DSM', 'DTW', 'DVL', 'EAR',
            'EAU', 'ECP', 'EGE', 'EKO', 'ELM', 'ELP', 'ERI', 'ESC', 'EUG',
            'EVV', 'EWN', 'EWR', 'EYW', 'FAI', 'FAR', 'FAT', 'FAY', 'FCA',
            'FLG', 'FLL', 'FNT', 'FSD', 'FSM', 'FWA', 'GCC', 'GCK', 'GEG',
            'GFK', 'GGG', 'GJT', 'GNV', 'GPT', 'GRB', 'GRI', 'GRK', 'GRR',
            'GSO', 'GSP', 'GTF', 'GTR', 'GUC', 'GUM', 'HDN', 'HGR', 'HHH',
            'HIB', 'HLN', 'HNL', 'HOB', 'HOU', 'HPN', 'HRL', 'HSV', 'HTS',
            'HVN', 'HYS', 'IAD', 'IAG', 'IAH', 'ICT', 'IDA', 'ILM', 'IMT',
            'IND', 'INL', 'ISP', 'ITH', 'ITO', 'JAC', 'JAN', 'JAX', 'JFK',
            'JLN', 'JMS', 'JNU', 'KOA', 'KTN', 'LAN', 'LAR', 'LAS', 'LAW',
            'LAX', 'LBB', 'LBE', 'LBF', 'LBL', 'LCH', 'LCK', 'LEX', 'LFT',
            'LGA', 'LGB', 'LIH', 'LIT', 'LNK', 'LRD', 'LSE', 'LWB', 'LWS',
            'LYH', 'MAF', 'MBS', 'MCI', 'MCO', 'MDT', 'MDW', 'MEI', 'MEM',
            'MFE', 'MFR', 'MGM', 'MHK', 'MHT', 'MIA', 'MKE', 'MKG', 'MLB',
            'MLI', 'MLU', 'MMH', 'MOB', 'MOT', 'MQT', 'MRY', 'MSN', 'MSO',
            'MSP', 'MSY', 'MTJ', 'MYR', 'OAJ', 'OAK', 'OGD', 'OGG', 'OGS',
            'OKC', 'OMA', 'OME', 'ONT', 'ORD', 'ORF', 'ORH', 'OTH', 'OTZ',
            'OWB', 'PAE', 'PAH', 'PBG', 'PBI', 'PDX', 'PGD', 'PHF', 'PHL',
            'PHX', 'PIA', 'PIB', 'PIE', 'PIH', 'PIR', 'PIT', 'PLN', 'PNS',
            'PPG', 'PRC', 'PSC', 'PSE', 'PSG', 'PSM', 'PSP', 'PUB', 'PVD',
            'PVU', 'PWM', 'RAP', 'RDD', 'RDM', 'RDU', 'RFD', 'RHI', 'RIC',
            'RIW', 'RKS', 'RNO', 'ROA', 'ROC', 'ROW', 'RST', 'RSW', 'SAF',
            'SAN', 'SAT', 'SAV', 'SBA', 'SBN', 'SBP', 'SCC', 'SCE', 'SCK',
            'SDF', 'SEA', 'SFB', 'SFO', 'SGF', 'SGU', 'SHD', 'SHR', 'SHV',
            'SIT', 'SJC', 'SJT', 'SJU', 'SLC', 'SLN', 'SMF', 'SMX', 'SNA',
            'SPI', 'SPN', 'SPS', 'SRQ', 'STC', 'STL', 'STS', 'STT', 'STX',
            'SUN', 'SUX', 'SWF', 'SWO', 'SYR', 'TLH', 'TOL', 'TPA', 'TRI',
            'TTN', 'TUL', 'TUS', 'TVC', 'TWF', 'TXK', 'TYR', 'TYS', 'UIN',
            'USA', 'VEL', 'VLD', 'VPS', 'WRG', 'XNA', 'XWA', 'YAK', 'YUM']
AIRLINES = [19393, 19690, 19790, 19805, 19930, 19977, 20304, 20363, 20366,
            20368, 20378, 20397, 20398, 20409, 20416, 20436, 20452]

class UI(tk.Tk, Observer):
    def __init__ (self, controller, model:FlightDataModel) -> None:
        super().__init__()
        self.title('Flight within USA displayer')
        self.__controller = controller
        self.__model = model
        self.__tabs = {}
        self.default_font = font.nametofont('TkDefaultFont')
        self.default_font.configure(family='Arial TUR', size=12)
        self.init_components()

    @property
    def controller(self):
        return self.__controller

    @property
    def model(self):
        return self.__model

    @property
    def notebook(self):
        return self.__notebook

    def init_components(self):
        self.__notebook = ttk.Notebook(self)
        flight_tab = FlightTab(self, self.controller)
        self.__notebook.add(flight_tab, text="Search by Flight")
        self.__tabs["Search by Flight"] = flight_tab
        self.__notebook.add(ExitTab(self), text="Exit")
        self.__notebook.pack(expand=True, fill="both")
        self.__notebook.bind('<<NotebookTabChanged>>', self.on_tab_change)
        
    def on_tab_change(self, event):
        tab = event.widget.tab('current')['text']
        if tab == 'Exit':
            self.destroy()

    def get_cur_tab(self):
        tab_text = self.notebook.tab(self.notebook.select(), "text")
        return self.__tabs[tab_text]

    def run(self):
        self.mainloop()

    def update(self, *args):
        if self.model.sel_graph == "average delay":
            self.get_cur_tab().graph.plot_graph(self.model.avg_delay)

class FlightTab(tk.Frame):
    def __init__(self, parent, controller, **kwargs) -> None:
        super().__init__(parent, **kwargs)
        self.controller = controller
        self.init_components()
        
    def init_components(self):
        left_frame = tk.Frame(self)
        self.graph = GraphFrame(left_frame)
        self.sort_bar = SortBar(self)
        self.sort_bar.add_cb_boxes("Origin Airport:", AIRPORTS)
        self.sort_bar.add_cb_boxes("Destination Airport:", AIRPORTS)
        self.sort_bar.add_checkboxes()
        self.avg_delay = tk.Button(left_frame, text="Average Delay", command=self.handle_button)
        self.graph.pack(side="top", fill="both", expand=True)
        self.sort_bar.pack(side="right", padx=10)
        self.avg_delay.pack(side="bottom")
        left_frame.pack(side="left", fill="both", expand=True)

    def get_selected_a(self):
        filt = []
        for combo_box in self.sort_bar.cb_list:
            filt.append(combo_box.cb_val)
        return filt

    def get_selected_wk(self):
        return self.sort_bar.checkboxes.week_var

    def get_selected_tb(self):
        return self.sort_bar.checkboxes.time_blk_var

    def handle_button(self, *args):
        a_code = self.get_selected_a()
        wk = self.get_selected_wk()
        tb = self.get_selected_tb()
        self.controller.avg_delay_flight(a_code, wk, tb)

class ExitTab(tk.Frame):
    def __init__(self, parent, **kwargs) -> None:
        super().__init__(parent, **kwargs)

    def init_components(self):
        pass

class SortBar(tk.Frame):
    def __init__(self, parent, **kwargs) -> None:
        super().__init__(parent, **kwargs)
        self.__cb_list = []

    @property
    def cb_list(self):
        return self.__cb_list

    @property
    def checkboxes(self):
        return self.__checkboxes

    def add_cb_boxes(self, label: str, load: list):
        cb_frame = ComboboxFrame(self, label, load)
        self.__cb_list.append(cb_frame)
        cb_frame.pack()
    
    def add_checkboxes(self):
        self.__checkboxes = CheckBoxFrame(self)
        self.__checkboxes.pack()

class CheckBoxFrame(tk.Frame):
    WEEK = ["Week 1", "Week 2", "Week 3", "Week 4", "Week 5"]
    TIME_BLK = ["Early Morning", "Morning", "Afternoon", "Evening", "Night"]
    
    def __init__(self, parent, **kwargs) -> None:
        super().__init__(parent, **kwargs)
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
        week_label = tk.Label(self,text="Week of the month:")
        week_label.pack(anchor="w")
        for _ in range(5):
            checkbox = tk.Checkbutton(self, text=self.WEEK[_], variable=self.__week_var[_])
            checkbox.pack(anchor="w")
        time_blk_label = tk.Label(self,text="Departure time block:")
        time_blk_label.pack(anchor="w")
        for _ in range(5):
            checkbox = tk.Checkbutton(self, text=self.TIME_BLK[_], variable=self.__time_blk_var[_])
            checkbox.pack(anchor="w")        

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
        self.init_components()

    def init_components(self):
        self.__fig = Figure()
        self.__canvas = FigureCanvasTkAgg(self.__fig, self)
        toolbar = NavigationToolbar2Tk(self.__canvas, self)
        toolbar.update()
        self.__canvas.get_tk_widget().pack(side="top", fill="both", expand=True)

    def plot_graph(self, data):
        fig = Figure()
        ax = fig.subplots()
        sns.lineplot(data=data, ax=ax)
        self.__canvas.figure = fig
        self.__canvas.draw()
