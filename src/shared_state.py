from PySide6.QtCore import QDate

class SharedState:
    def __init__(self):
        self.selected_hotel = ""
        self.selected_season = "Baja"
        self.selected_check_in = QDate.currentDate()
        self.selected_check_out = QDate.currentDate().addDays(1)
        self.observers = []

    def add_observer(self, observer):
        self.observers.append(observer)

    def notify_observers(self, property_name):
        for observer in self.observers:
            if hasattr(observer, f"on_{property_name}_changed"):
                getattr(observer, f"on_{property_name}_changed")(getattr(self, f"selected_{property_name}"))

    @property
    def hotel(self):
        return self.selected_hotel

    @hotel.setter
    def hotel(self, value):
        self.selected_hotel = value
        self.notify_observers("hotel")

    @property
    def season(self):
        return self.selected_season

    @season.setter
    def season(self, value):
        self.selected_season = value
        self.notify_observers("season")

    @property
    def check_in(self):
        return self.selected_check_in

    @check_in.setter
    def check_in(self, value):
        self.selected_check_in = value
        self.notify_observers("check_in")

    @property
    def check_out(self):
        return self.selected_check_out

    @check_out.setter
    def check_out(self, value):
        self.selected_check_out = value
        self.notify_observers("check_out") 