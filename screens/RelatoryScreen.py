from textual.screen import Screen
from textual.widgets import Header, Footer, Label, Select, Input, Button
from textual.containers import VerticalScroll, Container, Horizontal, Center

from widgets.Relatory.filter import Filter
from widgets.Relatory.ordenation import Ordenation
from widgets.Relatory.period import Period
from widgets.Relatory.columns import Columns

class RelatoryScreen(Screen):
    BINDINGS = [
        ('escape', 'app.pop_screen', "Voltar"),
    ]

    def compose(self):
        yield Header(show_clock=True, icon=":book:")

        with VerticalScroll(id="mainRelatory"):
            with Center(id="period", classes="sectionRelatory"):
                yield Period()
            with Center(id="ordenation", classes="sectionRelatory"):
                yield Ordenation()
            with Center(id="filterRelatory", classes="sectionRelatory"):
                yield Filter()
            with Center(id="columnsRelatory", classes="sectionRelatory"):
                yield Columns()
            with Horizontal():
                yield Button("Baixar", classes="relatoryButton")
                yield Button("Imprimir", classes="relatoryButton")
            
        yield Footer()

    def _on_mount(self):
        period = self.app.query_one("#period")
        ordenation = self.app.query_one("#ordenation")
        filterrl = self.app.query_one("#filterRelatory")
        columns = self.app.query_one("#columnsRelatory")

        period.border_title = "Período"
        ordenation.border_title = "Ordenação"
        filterrl.border_title = "Filtros"
        columns.border_title = "Colunas"
        