"""Controller for Flight within USA displayer"""
from model import FlightDataModel
from view import UI

class Controller:
    def __init__(self) -> None:
        self.__model = FlightDataModel()
        self.__view = UI(self, self.__model)

    def run(self):
        self.__view.run()
