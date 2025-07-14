from textual import on
from textual.widgets import Static, Input, Button
from textual.containers import HorizontalScroll


class ChangeAccount(Static):
    def compose(self):
        bank = Input(placeholder="***", max_length=3, type="integer", id="bank", classes="addorremove")
        agency = Input(placeholder="**", max_length=2, type="integer", id="agency", classes="addorremove")
        name = Input(placeholder=":", type="text", max_length=30, id="name", classes="addorremove")
        balance = Input(placeholder="R$ **_***.**", max_length=32, type="number", id="balance", classes="addorremove")

        bank.border_title = "Banco"
        agency.border_title = "Ag"
        name.border_title = "Descrição do Banco"
        balance.border_title = "Saldo"

        with HorizontalScroll(classes="changeAccount"):
            yield bank
            yield agency
            yield name
            yield balance
            yield Button("[b red]X[/]", id="remove")