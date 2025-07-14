from textual.widgets import Static, Input, Label, Button
from textual.suggester import SuggestFromList
from textual.containers import Grid
from textual import on

class Conference(Static):
    def compose(self):
        with Grid(id="conf"):
            yield Input(placeholder="***", max_length=3, type="integer", id="bankconf")
            yield Input(placeholder="**", max_length=2, type="integer", id="agencyconf")
            yield Label(id="balance")
            yield Input(placeholder="****", type="number", id="valueconf")
            yield Label(id='result')
            yield Button("Limpar", id="clearconf")

    def _on_mount(self):
        bank = self.query_one("#bankconf")
        agency = self.query_one("#agencyconf")
        value = self.query_one("#valueconf")
        res = self.query_one("#result")
        clear = self.query_one("#clearconf")
        balance = self.query_one("#balance")
        self.changed = False

        bank.border_title = "Banco"
        agency.border_title = "Ag"
        value.border_title = "Valor de comparação"
        res.border_title = "Diferença"
        balance.border_title = "Saldo"

        res.display = "none"
        balance.display = "none"
        clear.display = "none"

        bank.suggester = SuggestFromList(self.app.BANK_NUMBERS)
        agency.suggester = SuggestFromList(self.app.AGENCY_NUMBERS)

    @on(Input.Submitted)
    def verify(self):
        bank = str(self.query_one("#bankconf").value).zfill(3)
        agency = str(self.query_one("#agencyconf").value).zfill(2)
        value = str(self.query_one("#valueconf").value)
        result = self.query_one("#result")
        balanceInp = self.query_one("#balance")
        clear = self.query_one("#clearconf")

        if (bank, agency) not in self.app.NUMBERS:
            self.app.notify("Não existe conta associada a esse banco e agência.", severity="error")
            return
        
        try:
            value = float(value)
        except:
            self.app.notify("Valor deve ser um número no formato R$ **_****.**", severity="error")
            return
        
        balance = float(".".join(map(str, self.app.ACCOUNT.getBalance(bank, agency))))

        difference = balance - value

        result.display = "block"
        balanceInp.display = "block"
        clear.display = "block"
        balanceInp.update(f"{balance}")

        if difference == 0.0:
            result.update("[green bold]Saldo OK[/]")
        else:
            result.update(f"[red bold]{difference:.2f}[/]")

        self.changed = True

    @on(Button.Pressed)
    def clear(self):
        bank = self.query_one("#bankconf")
        agency = self.query_one("#agencyconf")
        value = self.query_one("#valueconf")
        result = self.query_one("#result")
        balance = self.query_one("#balance")
        clear = self.query_one("#clearconf")

        result.display = "none"
        clear.display = "none"
        balance.display = "none"

        bank.value = ""
        agency.value = ""
        value.value = ""

        self.changed = False

    @on(Input.Changed)
    def clearInput(self):
        if self.changed:
            result = self.query_one("#result")
            clear = self.query_one("#clearconf")
            balance = self.query_one("#balance")

            result.display = "none"
            clear.display = "none"
            balance.display = "none"
            self.changed = False