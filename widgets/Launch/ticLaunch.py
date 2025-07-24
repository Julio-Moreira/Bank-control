from textual import on
from textual.widgets import Static, Input, Button, DataTable, Select, Label
from rich.text import Text
from textual.containers import HorizontalScroll, Vertical
from textual.suggester import SuggestFromList

from screens.TicConfirmScreen import TicConfirmScreen
from widgets.Launch.listLaunch import ListLaunch

from datetime import datetime


class TicLaunch(Static):
    def compose(self):
        with Vertical(id="ticScreen"):
            with HorizontalScroll(id="inputsTic"):
                yield Input(placeholder="***", max_length=3, type="integer", id="bankTic", classes="inputtic")
                yield Input(placeholder="*", max_length=2, type="integer", id="agTic", classes="inputtic")
                yield Input(placeholder="*****", max_length=10, type="integer", id="numberTic", classes="inputtic")
                yield Button(label="Adicionar", variant="success", id="addTic")
                yield Label(" ")
                yield Button(label="Limpar", id="clearTic")
            yield DataTable(id="TicLaunchTable")
            yield Button(label="Confirmar", variant="default", id="confirmTic")

    def _on_mount(self):
        self.launches = []

        bank = self.app.query_one("#bankTic")
        agency = self.app.query_one("#agTic")
        number = self.app.query_one("#numberTic")

        bank.border_title = "Banco"
        agency.border_title = "Ag"
        number.border_title = "Número"

        bank.suggester = SuggestFromList(self.app.BANK_NUMBERS)
        agency.suggester = SuggestFromList(self.app.AGENCY_NUMBERS)
        number.suggester = SuggestFromList(list(map(lambda x: x[2], self.app.LAUNCH_NUMBERS)))

        self.sortAscending = True
        self.sortColumn = None
        self.table = self.app.query_one("#TicLaunchTable")
        self.table.border_title = "Lançamentos incluidos"
        self.table.add_column(Text("Banco", style="bold", justify="center"), key="ticbank")
        self.table.add_column(Text("+", style="yellow"), key="ticsep1", width=1)
        self.table.add_column(Text("Agência", style="bold", justify="center"), key="ticagency")
        self.table.add_column(Text("+", style="yellow"), key="ticsep2", width=1)
        self.table.add_column(Text("Número", style="bold", justify="center"), key="ticnumber")
        self.table.add_column(Text("+", style="yellow"), key="ticsep3", width=1)
        self.table.add_column(Text("Tipo", style="bold", justify="center"), key="tictyp")
        self.table.add_column(Text("+", style="yellow"), key="ticsep4", width=1)
        self.table.add_column(Text("Histórico", style="bold", justify="center"), key="tichistory")
        self.table.add_column(Text("+", style="yellow"), key="ticsep5", width=1)
        self.table.add_column(Text("Ticado", style="bold", justify="center"), key="tictic")
        self.table.add_column(Text("+", style="yellow"), key="ticsep7", width=1)
        self.table.add_column(Text("Valor (R$)", style="bold", justify="center"), key="ticvalue")
        self.refreshTable()

    @on(Button.Pressed, "#addTic")
    @on(Input.Submitted)
    def addPressed(self):
        bank = self.app.query_one("#bankTic").value
        agency = self.app.query_one("#agTic").value
        number = self.app.query_one("#numberTic").value

        if not self.validateBank(bank): 
            self.app.notify("Campo banco deve ser um número de 3 digitos", severity="error")
            return
        
        bank = str(bank).zfill(3)

        if not self.validateAgency(agency):
            self.app.notify("Campo agência deve ser um número de 1 digito", severity="error")
            return
        elif (bank, agency) not in self.app.NUMBERS:
            self.app.notify("Não existe conta associada a esse banco e agência.", severity="error")
            return
        elif not self.validateNumber(number):
            self.app.notify("Campo número deve ser um número com pelo menos 1 caracter", severity="error")
            return
        elif (bank, agency, number) not in self.app.LAUNCH_NUMBERS:
            self.app.notify("Esse lançamento não existe", severity="error")
            return
        
        typ, valueIntPart, valueDecimalPart,History, IsChecked, _, _, _ = self.app.LAUNCH.getLaunch(number,agency,bank)

        self.launches.append([bank, agency, number, typ, History, IsChecked, f"{valueIntPart},{valueDecimalPart:02d}"])
        self.refreshTable(self.launches)
        self.app.query_one("#bankTic").value = ''
        self.app.query_one("#agTic").value = ''
        self.app.query_one("#numberTic").value = ''
    
    @on(Button.Pressed, "#confirmTic")
    def confirmPressed(self):
        def confirm(res) -> None:
            match res:
                case "T":
                    self.app.LAUNCH.tic(True, [x[:3] for x in self.launches])
                case "N":
                    self.app.LAUNCH.tic(False, [x[:3] for x in self.launches])
                case "D":
                    self.app.LAUNCH.deleteLaunches([x[:3] for x in self.launches], self.app.ACCOUNT, self.app.LAUNCH)

            self.launches = []
            self.refreshTable()
            self.app.query_one(ListLaunch).refreshTable()

        if self.launches == []:
            self.app.notify("Adicione algum lançamento para tomar alguma ação", severity="error")
            return

        self.app.push_screen(TicConfirmScreen(), confirm)

    @on(Button.Pressed, "#clearTic")
    def clearPressed(self):
        self.refreshTable()

    def validateBank(self, bank):
        return bank.isdigit() and len(bank) == 3

    def validateAgency(self, agency):
        return agency.isdigit() and len(agency) > 0

    def validateNumber(self, number):
        return number.isdigit() and len(str(number).strip()) > 0

    def refreshTable(self, launches=None):
        self.table.clear()
        self.table.loading = True
        
        if launches is None:    
            clear = self.app.query_one("#clearTic")
            clear.display = "none"

            self.table.add_row(
                Text(f"***", style="bold", justify="center"), Text("+", style="bold yellow"),
                Text(f"**", style="bold", justify="center"), Text("+", style="bold yellow"),
                Text(f" - ", style="bold", justify="center"), Text("+", style="bold yellow"),
                Text(f"**", justify="center"), Text("+", style="bold yellow"),
                Text(f" - ", justify="center"), Text("+", style="bold yellow"),
                Text(f" - ", justify="center"), Text("+", style="bold yellow"),
                Text(f" - ", style="bold", justify="left")
            )       
            self.table.loading = False

            return

        clear = self.app.query_one("#clearTic")
        clear.display = "block"

        if self.sortColumn is not None:
            launches.sort(key=lambda x: x[self.sortColumn], reverse=not self.sortAscending)

        for launch in launches:
            bank, agency, number, typ, History, IsChecked, value = launch
            ticado = ("*", "green") if IsChecked == 1 else ("-", "red")

            self.table.add_row(
                Text(f"{str(bank).zfill(3)}", style="bold", justify="center"), Text("|", style="bold yellow"),
                Text(f"{str(agency).zfill(2)}", style="bold", justify="center"), Text("|", style="bold yellow"),
                Text(f"{number}", style="bold", justify="left"), Text("|", style="bold yellow"),
                Text(f"{typ}", justify="center"), Text("|", style="bold yellow"),
                Text(f"{History}", justify="left"), Text("|", style="bold yellow"),
                Text(f"{ticado[0]}", style=f"{ticado[1]}", justify="center"), Text("|", style="bold yellow"),
                Text(f"{value}", style="bold", justify="right")
            )
        self.table.loading = False

    @on(DataTable.HeaderSelected)
    def sort_table(self, event):
        column_map = {
            "bank": self.action_sort_by_bank,
            "agency": self.action_sort_by_agency,
            "number": self.action_sort_by_number,
            "sit": self.action_sort_by_sit,
            "tic": self.action_sort_by_tic,
            "value": self.action_sort_by_value,
            "movdate": self.action_sort_by_movdate,
            "emdate": self.action_sort_by_emdate,
        }
        if event.column_key in column_map:
            column_map[event.column_key]()

    def toggle_sort(self, key):
        if not hasattr(self, "sort_state"):
            self.sort_state = {}
        self.sort_state[key] = not self.sort_state.get(key, False)
        return self.sort_state[key]

    def action_sort_by_bank(self):
        self.table.sort("bank", key=lambda x: x.plain, reverse=self.toggle_sort("bank"))

    def action_sort_by_agency(self):
        self.table.sort("agency", key=lambda x: x.plain, reverse=self.toggle_sort("agency"))

    def action_sort_by_number(self):
        self.table.sort("number", key=lambda x: int(x.plain), reverse=self.toggle_sort("number"))

    def action_sort_by_value(self):
        self.table.sort("value", key=lambda x: float(str(x.plain).replace(".", "").replace(",", ".")), reverse=self.toggle_sort("value"))

    def action_sort_by_movdate(self):
        self.table.sort("movdate", key=lambda x: datetime.strptime(x.plain, "%d/%m/%y"), reverse=self.toggle_sort("movdate"))

    def action_sort_by_emdate(self):
        self.table.sort("emdate", key=lambda x: datetime.strptime(x.plain, "%d/%m/%y"), reverse=self.toggle_sort("emdate"))

    def action_sort_by_sit(self):
        """Ordena pela situação (Lançado ou Não Lançado)."""
        self.table.sort("sit", key=lambda x: x.plain, reverse=self.toggle_sort("sit"))

    def action_sort_by_tic(self):
        """Ordena pela marcação de ticado (* ou _)."""
        self.table.sort("tic", key=lambda x: x.plain, reverse=self.toggle_sort("tic"))
    