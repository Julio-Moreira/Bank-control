from textual import on
from textual.widgets import Static, Input, Checkbox, Label, Button
from textual.containers import HorizontalScroll, Vertical

class Columns(Static):
    def compose(self):
       yield Label("colunas")

    def _on_mount(self):
        pass