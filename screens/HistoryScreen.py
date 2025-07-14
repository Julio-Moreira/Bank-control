from textual.screen import Screen
from textual.widgets import Header, Footer, Label
from textual.containers import Horizontal
from widgets.SideBar import SideBar


class HistoryScreen(Screen):
    BINDINGS = [
        ('escape', 'app.pop_screen', "Voltar"),
    ]

    def compose(self):
        yield Header(show_clock=True, icon=":bookmark_tabs:")
        yield Label(":construction:", classes="wip")
        yield Footer()
