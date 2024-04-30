"""Model to handle data processing for Flight within USA displayer"""
from __future__ import annotations
import os
import pandas as pd
from abc import ABC, abstractmethod

class Subject(ABC):
    """
    Abstract class for subject to be observed
    """
    @abstractmethod
    def attach(self, observer: Observer):
        """
        Attach an observer to the subject
        """
        pass
    
    @abstractmethod
    def detach(self, observer: Observer):
        """
        Detach an observer from the subject
        """
        pass
    
    @abstractmethod
    def notify(self):
        """
        Notify observers about an event
        """
        pass

class Observer(ABC):
    """
    Abstract class for observer
    """
    @abstractmethod
    def update(self, subject: Subject):
        """
        Recieve update from subject
        """
        pass

class FlightDataModel(Subject):
    """
    Model for computing data from the datasets
    """
    _observers : list[Observer] =  []
    
    def __init__(self) -> None:
        self.__df = self.gen_df()
        self.__sorted_df: pd.DataFrame
        self.__states = [SearchByFlight(self.__df),
                         SearchByAirport(self.__df),
                         SearchByAirline(self.__df)]
        self.__graph_type = ["average delay",
                             "% on-time",
                             "% time blk"]
        self.__current_state = self.__states[0]
        self.__sel_graph = self.__graph_type[0]
    
    @property
    def df(self):
        return self.__df

    @property
    def sorted_df(self):
        return self.__sorted_df

    @property
    def graph_type(self):
        return self.__graph_type

    def gen_df(self):
        """
        Read csv files as dataframe, join them and clean the data.
        Return: a dataframe consists of data from 2 datasets
        """
        df1 = pd.read_csv(os.path.join(os.getcwd(), "datasets/Jan_2020_ontime.csv"))
        df2 = pd.read_csv(os.path.join(os.getcwd(), "datasets/Airline_dataset.csv"))
        df1["ORIGIN"] = df1["ORIGIN"].str.replace('"','')
        df1["DEST"] = df1["DEST"].str.replace('"','')
        df2["FL_DATE"] = pd.to_datetime(df2["FL_DATE"], format="%m/%d/%y")
        df1["FL_DATE"] = "1/" + df1["DAY_OF_MONTH"].astype(str) + "/20"
        df1["FL_DATE"] = pd.to_datetime(df1["FL_DATE"], format="%m/%d/%y")
        df3 = pd.merge(df1, df2, how="left",
                             left_on=["ORIGIN","DEST","DEP_TIME","ARR_TIME","FL_DATE"],
                             right_on=["ORIGIN_AIRPORT","DEST_AIRPORT","DEP_TIME","ARR_TIME","FL_DATE"])
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
        self._observers.append(observer)

    def detach(self, observer: Observer):
        self._observers.remove(observer)

    def notify(self):
        for observer in self._observers:
            observer.update(self)
    
    def set_state(self, index: int):
        self.__current_state = self.__states[index]

    def set_sel_graph(self, index: int):
        self.__sel_graph = self.__graph_type[index]

    def sort_data(self, a_code: list[str], week: list[bool],
                         time_blk: list[bool]):
        self.__sorted_df = self.__current_state.sort_data(a_code, week, time_blk)

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
    def sort_data(self):
        """
        Return a sorted dataframe based on the filter.
        """
        pass

class SearchByFlight(SearchState):
    def sort_data(self, flight: list[str], week: list[bool], time_blk: list[bool]):
        selected_wk, selected_time_blk = self.convert_bool_to_filter(week,time_blk)
        return self.df.loc[(self.df["ORIGIN"] == flight[0]) &
                            (self.df["DEST"] == flight[1]) &
                            (self.df["WEEK"].isin(selected_wk)) &
                            (self.df["DEP_TIME_BLK"].isin(selected_time_blk))]

class SearchByAirport(SearchState):
    def sort_data(self, airport: list[str], week: list[bool], time_blk: list[bool]):
        selected_wk, selected_time_blk = self.convert_bool_to_filter(week,time_blk)
        return self.df.loc[(self.df["ORIGIN"] == airport[0]) &
                           (self.df["WEEK"].isin(selected_wk)) &
                           (self.df["DEP_TIME_BLK"].isin(selected_time_blk))]

class SearchByAirline(SearchState):
    def sort_data(self, airline: list[int], week:list[bool], time_blk: list[bool]):
        selected_wk, selected_time_blk = self.convert_bool_to_filter(week,time_blk)
        return self.df.loc[(self.df["OP_CARRIER_AIRLINE_ID"] == airline[0]) &
                           (self.df["WEEK"].isin(selected_wk)) &
                           (self.df["DEP_TIME_BLK"].isin(selected_time_blk))]


if __name__ == "__main__":
    data = FlightDataModel()
    data.set_state(2)
    data.sort_data([20366], [True,False,False,False,False], [True,True,True,True,True])
    print(data.sorted_df)
