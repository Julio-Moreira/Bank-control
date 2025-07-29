from textual import on
from textual.widgets import Static, Input, Checkbox, Label, Button
from textual.containers import HorizontalScroll, Vertical

class Ordenation(Static):
    def compose(self):
       yield Label("ord")

    def _on_mount(self):
        pass