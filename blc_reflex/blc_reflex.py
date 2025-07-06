
from abc import ABC, abstractmethod
import reflex as rx


class State(rx.State):
    count: int = 0

    def increment(self):
        self.count += 1

    def decrement(self):
        self.count -= 1


class InputField:
    pass

class Weight(ABC):
    pass

class Plate(Weight):
    pass

class Barbell(Weight):
    pass


def index():
    return rx.box(
        rx.text("This is a page"),
        # Reference components defined in other functions.
    )



app = rx.App()
app.add_page(index)
