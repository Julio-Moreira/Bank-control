from textual.screen import Screen
from textual.widgets import LoadingIndicator, Header, Footer

class LoadingScreen(Screen):
    def compose(self):
        yield Header()
        yield LoadingIndicator()
        yield Footer()