"""Model to handle data processing for Flight within USA displayer"""
from __future__ import annotations
from abc import ABC, abstractmethod
import os
import pandas as pd

class Subject(ABC):
    """
    Abstract class for subject to be observed
    """
    @abstractmethod
    def attach(self, observer: Observer):
        """
        Attach an observer to the subject
        """
        raise NotImplementedError

    @abstractmethod
    def detach(self, observer: Observer):
        """
        Detach an observer from the subject
        """
        raise NotImplementedError

    @abstractmethod
    def notify(self):
        """
        Notify observers about an event
        """
        raise NotImplementedError

class Observer(ABC):
    """
    Abstract class for observer
    """
    @abstractmethod
    def update(self, subject: Subject):
        """
        Recieve update from subject
        """
        raise NotImplementedError

class FlightDataModel(Subject):
    """
    Model for computing data from the datasets
    """
    def __init__(self) -> None:
        self.__df = self.gen_df()
        self.__sorted : pd.DataFrame
        self.__series : pd.Series
        self.__info : str
        self.__states = [SearchByFlight(self.__df),
                         SearchByAirport(self.__df),
                         SearchByAirline(self.__df)]
        self.__current_state: SearchState = self.__states[0]
        self.observers = []

    @property
    def df(self):
        """
        Getter for df attribute
        """
        return self.__df

    @property
    def sorted(self):
        """
        Getter for sorted attribute
        """
        return self.__sorted

    @sorted.setter
    def sorted(self, value):
        """
        Setter for sorted attribute
        """
        self.__sorted = value

    @property
    def series(self):
        """
        Getter for series attribute
        """
        return self.__series

    @series.setter
    def series(self, value):
        """
        Setter for series attribute
        """
        self.__series = value

    @property
    def info(self):
        """
        Getter for info attribute
        """
        return self.__info

    @info.setter
    def info(self, value):
        """
        Setter for info attribute
        """
        self.__info = value

    def gen_df(self):
        """
        Read csv files as dataframe, join them and clean the data.
        Return: a dataframe consists of data from 2 datasets
        """
        df1 = pd.read_csv(os.path.join(os.getcwd(), "datasets", "Jan_2020_ontime.csv"))
        df2 = pd.read_csv(os.path.join(os.getcwd(), "datasets", "Airline_dataset.csv"))
        df1["ORIGIN"] = df1["ORIGIN"].str.replace('"','')
        df1["DEST"] = df1["DEST"].str.replace('"','')
        df2["FL_DATE"] = pd.to_datetime(df2["FL_DATE"], format="%m/%d/%y")
        df1["FL_DATE"] = "1/" + df1["DAY_OF_MONTH"].astype(str) + "/20"
        df1["FL_DATE"] = pd.to_datetime(df1["FL_DATE"], format="%m/%d/%y")
        df3 = pd.merge(df1, df2, how="left",
                             left_on=["ORIGIN","DEST","DEP_TIME","ARR_TIME","FL_DATE"],
                             right_on=["ORIGIN_AIRPORT","DEST_AIRPORT","DEP_TIME",
                                       "ARR_TIME","FL_DATE"])
        df3["DEP_TIME_BLK"] = ["Early Morning" if 400 <= x < 800 else
                               ("Morning" if 800 <= x < 1200 else
                                ("Afternoon" if 1200 <= x < 1600 else
                                 ("Evening" if 1600 <= x < 1900 else
                                  ("Night" if x >= 1900 or x < 400 else None))))
                               for x in df3["DEP_TIME"]]
        df3["WEEK"] = df3["FL_DATE"].dt.isocalendar().week
        df3["STATUS"] = ["Delayed" if x1 else
                         ("Diverted" if x2 else
                          ("Canceled" if x3 else "On-time"))
                         for x1, x2, x3 in zip(df3["DEP_DEL15"],
                                               df3["DIVERTED"],
                                               df3["CANCELLED"])]
        df3.drop(df3.columns[df3.columns.str.contains('unnamed',case = False)],
                       axis=1, inplace=True)
        df3.drop(["AIRLINE_ID","ORIGIN_AIRPORT","DEST_AIRPORT"], axis=1, inplace=True)
        return df3

    def attach(self, observer: Observer):
        self.observers.append(observer)

    def detach(self, observer: Observer):
        self.observers.remove(observer)

    def notify(self):
        for observer in self.observers:
            observer.update()

    def set_state(self, index: int):
        """
        Set the model's search state
        """
        self.__current_state = self.__states[index]

    def get_avg_data(self, a_code: list[str], week: list[bool], time_blk: list[bool]):
        """
        Update the sorted attribute to a Series required to plot a line graph of average delays
        """
        self.sorted, self.series = self.__current_state.avg_flight_delay(a_code, week, time_blk)
        self.info = self.__current_state.get_info_str(self.sorted)
        self.notify()

    def get_on_time_data(self, a_code: list[str], week: list[bool], time_blk: list[bool]):
        """
        Update the sorted attribute to a Series required to plot a pie chart of percentage of
        flights departing on time, with delay, diverted, or canceled
        """
        self.sorted, self.series = self.__current_state.percent_on_time(a_code, week, time_blk)
        self.info = self.__current_state.get_info_str(self.sorted)
        self.notify()

    def get_time_blk_data(self, a_code: list[str], week: list[bool], time_blk: list[bool]):
        """
        Update the sorted attribute to a Series required to plot a pie chart of percentage of
        flights in each departure time block
        """
        self.sorted, self.series = self.__current_state.percent_time_block(a_code, week, time_blk)
        self.info = self.__current_state.get_info_str(self.sorted)
        self.notify()

    def get_data_story_telling_data(self):
        """
        Return a list consisted of descriptive statistics(string) and series needed to show the
        data story telling page
        """
        data_list = []
        dep_stats = list(self.df["DEP_DELAY"].describe().values)
        dep_median = self.df["DEP_DELAY"].median()
        dep_mode = self.df["DEP_DELAY"].mode().values
        arr_stats = list(self.df["ARR_DELAY"].describe().values)
        arr_median = self.df["ARR_DELAY"].median()
        arr_mode = self.df["ARR_DELAY"].mode()
        temp_str = (f"*Departure Delay Statistics*\n"
                    f"Mean:   {dep_stats[1]:.2f}\n"
                    f"Median: {dep_median:.2f}\n"
                    f"Mode:   {dep_mode[0]:.2f}\n"
                    f"Min:    {dep_stats[3]:.2f}\n"
                    f"Max:    {dep_stats[7]:.2f}\n"
                    f"VAR:    {dep_stats[2]**2:.2f}\n"
                    f"SD:     {dep_stats[2]:.2f}\n"
                    f"CV:     {dep_stats[2]/dep_stats[1]:.2f}\n"
                    f"IQR:    {dep_stats[6]-dep_stats[4]:.2f}\n\n"
                    f"*Arrival Delay Statistics*\n"
                    f"Mean:   {arr_stats[1]:.2f}\n"
                    f"Median: {arr_median:.2f}\n"
                    f"Mode:   {arr_mode[0]:.2f}\n"
                    f"Min:    {arr_stats[3]:.2f}\n"
                    f"Max:    {arr_stats[7]:.2f}\n"
                    f"VAR:    {arr_stats[2]**2:.2f}\n"
                    f"SD:     {arr_stats[2]:.2f}\n"
                    f"CV:     {arr_stats[2]/dep_stats[1]:.2f}\n"
                    f"IQR:    {arr_stats[6]-dep_stats[4]:.2f}\n\n")
        data_list.append(temp_str)
        return data_list

class SearchState(ABC):
    """
    Abstract class for state that contain the model's function
    """
    _time_blk_dict = {0: "Early Morning",
                      1: "Morning",
                      2: "Afternoon",
                      3: "Evening",
                      4: "Night"}

    def __init__(self, dataframe: pd.DataFrame) -> None:
        self._df = dataframe

    @property
    def df(self):
        """
        Getter for df attribute
        """
        return self._df

    def convert_bool_to_filter(self, week: list[bool], time_blk: list[bool]):
        """
        Convert list of boolean into list of filter option selected
        """
        wk = [i+1 for i in range(5) if week[i]]
        t_bk = [self._time_blk_dict[i] for i in range(5) if time_blk[i]]
        return wk, t_bk

    @abstractmethod
    def sort_data(self, filt: list[str], week: list[bool], time_blk: list[bool]):
        """
        Return a sorted dataframe using the parameters as the filter
        """
        raise NotImplementedError

    @abstractmethod
    def get_info_str(self, data: pd.DataFrame):
        """
        Return a string consisted of delay statistics and relevant information
        """
        raise NotImplementedError

    def avg_flight_delay(self, filt: list[str], week: list[bool], time_blk: list[bool]):
        """
        Return a Series object required to plot a line graph of average delays
        """
        temp_df = self.sort_data(filt, week, time_blk)
        temp_series = temp_df[["DEP_DELAY","ARR_DELAY","WEEK"]].groupby("WEEK").mean()
        return temp_df, temp_series

    def percent_on_time(self, filt: list[str], week: list[bool], time_blk: list[bool]):
        """
        Return a Series object required to plot a pie chart of percentage of flights
        departing on time, with delay, diverted, or canceled
        """
        temp_df = self.sort_data(filt, week, time_blk)
        temp_series = temp_df["STATUS"].value_counts()
        return temp_df, temp_series

    def percent_time_block(self, filt: list[str], week: list[bool], time_blk: list[bool]):
        """
        Reture a Series object required to plot a pie chart of percentage of flights
        in each departure time block
        """
        temp_df = self.sort_data(filt, week, time_blk)
        temp_series = temp_df["DEP_TIME_BLK"].value_counts()
        return temp_df, temp_series

class SearchByFlight(SearchState):
    """
    A state for sorting the dataframe using flight as the filter
    """
    def sort_data(self, filt: list[str], week: list[bool], time_blk: list[bool]):
        selected_wk, selected_time_blk = self.convert_bool_to_filter(week,time_blk)
        return self.df.loc[(self.df["ORIGIN"] == filt[0]) &
                            (self.df["DEST"] == filt[1]) &
                            (self.df["WEEK"].isin(selected_wk)) &
                            (self.df["DEP_TIME_BLK"].isin(selected_time_blk))]

    def get_info_str(self, data: pd.DataFrame):
        try:
            orgin_airport = data["ORIGIN"].unique()[0]
        except:
            return f"No flights found"
        dest_airport = data["DEST"].unique()[0]
        num_flights = data["ORIGIN"].count()
        dist = data["DISTANCE"].unique()[0]
        airlines_delay = data[["OP_CARRIER_AIRLINE_ID",
                               "DEP_DELAY",
                               "ARR_DELAY"]].groupby("OP_CARRIER_AIRLINE_ID").mean()
        dep_stat = list(data["DEP_DELAY"].describe().values)
        arr_stat = list(data["ARR_DELAY"].describe().values)
        airlines_id = airlines_delay.index
        airlines_dep = list(airlines_delay["DEP_DELAY"].values)
        airlines_arr = list(airlines_delay["ARR_DELAY"].values)
        airlines_info_list = []
        for count in range(len(airlines_id)):
            airlines_info_list.append((f"Airline ID: {airlines_id[count]}\n"
                                       f"AVG DEP Delay:"
                                       f" {airlines_dep[count]:.2f} min(s)\n"
                                       f"AVG ARR Delay:"
                                       f" {airlines_arr[count]:.2f} min(s)\n\n"))
        temp_str = (f"Flight from {orgin_airport} to {dest_airport}\n"
                    f"Distance: {dist} miles\n"
                    f"Number of Flight(s): {num_flights}\n\n"
                    f"*Departure Delay Statistics*\n"
                    f"Average Delay:  {dep_stat[1]:.2f} min(s)\n"
                    f"Shortest Delay: {dep_stat[3]:.2f} min(s)\n"
                    f"Longest Delay:  {dep_stat[7]:.2f} min(s)\n\n"
                    f"*Arrival Delay Statistics*\n"
                    f"Average Delay:  {arr_stat[1]:.2f} min(s)\n"
                    f"Shortest Delay: {arr_stat[3]:.2f} min(s)\n"
                    f"Longest Delay:  {arr_stat[7]:.2f} min(s)\n\n"
                    f"*Known Airline(s)*\n"
                    f"{''.join(airlines_info_list)}")
        return temp_str

class SearchByAirport(SearchState):
    """
    A state for sorting the dataframe using airport as the filter
    """
    def sort_data(self, filt: list[str], week: list[bool], time_blk: list[bool]):
        selected_wk, selected_time_blk = self.convert_bool_to_filter(week,time_blk)
        return self.df.loc[(self.df["ORIGIN"] == filt[0]) &
                           (self.df["WEEK"].isin(selected_wk)) &
                           (self.df["DEP_TIME_BLK"].isin(selected_time_blk))]

    def get_info_str(self, data: pd.DataFrame):
        try:
            airport = data["ORIGIN"].unique()[0]
        except:
            return f"No flights found"
        num_flights = data["ORIGIN"].count()
        airlines_delay = data[["OP_CARRIER_AIRLINE_ID",
                               "DEP_DELAY",
                               "ARR_DELAY"]].groupby("OP_CARRIER_AIRLINE_ID").mean()
        dep_stat = list(data["DEP_DELAY"].describe().values)
        arr_stat = list(data["ARR_DELAY"].describe().values)
        airlines_id = airlines_delay.index
        airlines_dep = list(airlines_delay["DEP_DELAY"].values)
        airlines_arr = list(airlines_delay["ARR_DELAY"].values)
        airlines_info_list = []
        for count in range(len(airlines_id)):
            airlines_info_list.append((f"Airline ID: {airlines_id[count]}\n"
                                       f"AVG DEP Delay:"
                                       f" {airlines_dep[count]:.2f} min(s)\n"
                                       f"AVG ARR Delay:"
                                       f" {airlines_arr[count]:.2f} min(s)\n\n"))
        temp_str = (f"Airport: {airport}\n"
                    f"Number of Flight(s): {num_flights}\n\n"
                    f"*Departure Delay Statistics*\n"
                    f"Average Delay:  {dep_stat[1]:.2f} min(s)\n"
                    f"Shortest Delay: {dep_stat[3]:.2f} min(s)\n"
                    f"Longest Delay:  {dep_stat[7]:.2f} min(s)\n\n"
                    f"*Arrival Delay Statistics*\n"
                    f"Average Delay:  {arr_stat[1]:.2f} min(s)\n"
                    f"Shortest Delay: {arr_stat[3]:.2f} min(s)\n"
                    f"Longest Delay:  {arr_stat[7]:.2f} min(s)\n\n"
                    f"*Known Airline(s)*\n"
                    f"{''.join(airlines_info_list)}")
        return temp_str

class SearchByAirline(SearchState):
    """
    A state for sorting the dataframe using airline as the filter
    """
    def sort_data(self, filt: list[str], week: list[bool], time_blk: list[bool]):
        selected_wk, selected_time_blk = self.convert_bool_to_filter(week,time_blk)
        return self.df.loc[(self.df["OP_CARRIER_AIRLINE_ID"] == list(map(float, filt))[0]) &
                           (self.df["WEEK"].isin(selected_wk)) &
                           self.df["DEP_TIME_BLK"].isin(selected_time_blk)]

    def get_info_str(self, data: pd.DataFrame):
        try:
            airline_id = data["OP_CARRIER_AIRLINE_ID"].unique()[0]
        except:
            return f"No flights found"
        num_flights = data["OP_CARRIER_AIRLINE_ID"].count()
        dep_stat = list(data["DEP_DELAY"].describe().values)
        arr_stat = list(data["ARR_DELAY"].describe().values)
        airports = data[["ORIGIN","DEST"]].groupby("ORIGIN").count()
        airports_id = airports.index
        airports_num_flight = airports["DEST"].values
        airports_info_list = []
        for count in range(len(airports_id)):
            airports_info_list.append((f"Airport ID: {airports_id[count]}\n"
                                       f"% of flights:"
                                       f" {airports_num_flight[count]:.0f} flight(s)\n\n"))
        temp_str = (f"Airline ID: {airline_id}\n"
                    f"Number of Flight(s): {num_flights}\n\n"
                    f"*Departure Delay Statistics*\n"
                    f"Average Delay:  {dep_stat[1]:.2f} min(s)\n"
                    f"Shortest Delay: {dep_stat[3]:.2f} min(s)\n"
                    f"Longest Delay:  {dep_stat[7]:.2f} min(s)\n\n"
                    f"*Arrival Delay Statistics*\n"
                    f"Average Delay:  {arr_stat[1]:.2f} min(s)\n"
                    f"Shortest Delay: {arr_stat[3]:.2f} min(s)\n"
                    f"Longest Delay:  {arr_stat[7]:.2f} min(s)\n\n"
                    f"*Known Airport(s)*\n"
                    f"{''.join(airports_info_list)}")
        return temp_str


if __name__ == "__main__":
    test = FlightDataModel()
    test.set_state(0)
    test.get_avg_data(["ABE", "ATL"], [True,True,True,True,True], [True,True,True,True,True])
    print(test.df["DEP_DELAY"].mode().values)
