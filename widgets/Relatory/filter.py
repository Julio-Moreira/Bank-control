from textual import on
from textual.widgets import Static, Input, Checkbox, Label, Button
from textual.containers import HorizontalScroll, Vertical

class Filter(Static):
    def compose(self):
       yield Label("filtro")

    def _on_mount(self):
        pass