from textual.screen import Screen
from textual.widgets import Header, Footer, Label
from textual.containers import Horizontal
from widgets.SideBar import SideBar


class RelatoryScreen(Screen):
    BINDINGS = [
        ('escape', 'app.pop_screen', "Voltar"),
    ]

    def compose(self):
        yield Header(show_clock=True, icon=":book:")
        yield Label(":construction:", classes="wip")
        yield Footer()