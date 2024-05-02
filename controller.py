"""Controller for Flight within USA displayer"""
from model import FlightDataModel
from view import UI

class Controller:
    def __init__(self) -> None:
        self.__model = FlightDataModel()
        self.__view = UI(self, self.__model)
        self.__model.attach(self.__view)

    def set_search_type(self, index: int):
        self.__model.set_state(index)

    def avg_delay_flight(self, filt, week, time_blk):
        self.__model.set_sel_graph(0)
        self.__model.get_avg_data(filt, week, time_blk)

    def percent_on_time(self, filt, week, time_blk):
        self.__model.set_sel_graph(1)
        self.__model.get_on_time_data(filt, week, time_blk)

    def percent_time_blk(self, filt, week, time_blk):
        self.__model.set_sel_graph(2)
        self.__model.get_time_blk_data(filt, week, time_blk)

    def run(self):
        self.__view.run()
