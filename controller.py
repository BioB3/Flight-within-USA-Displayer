"""Controller for Flight within USA displayer"""
from model import FlightDataModel
from view import UI

class Controller:
    def __init__(self) -> None:
        self.__model = FlightDataModel()
        self.__view = UI(self, self.__model)
        self.__model.attach(self.__view)

    def avg_delay_flight(self, filt, week, time_blk):
        self.__model.set_state(0)
        self.__model.set_sel_graph(0)
        self.__model.get_avg_data(filt, week, time_blk)

    def run(self):
        self.__view.run()
