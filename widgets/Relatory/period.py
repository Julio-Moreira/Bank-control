from textual import on
from textual.widgets import Static, Input, Checkbox, Label, Button, Select
from textual.containers import HorizontalScroll, Vertical

class Period(Static):
    def compose(self):
       yield Select([("Dia", "D"),("Mês", "M"), ("Ano", "A"), ("Período customizado", "P")], allow_blank=False, id="selectPeriod")
    #    yield Input(placeholder="**", type="integer", max_length=2, id="dayPeriod")
    #    yield Input(placeholder="**", type="integer", max_length=2, id="dayPeriod")
    #    yield Input(placeholder="**", type="integer", max_length=2, id="dayPeriod")

    def _on_mount(self):
        pass