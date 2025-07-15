from textual.widgets import Static, DataTable, Button, Input, Checkbox
from textual.containers import HorizontalScroll, VerticalScroll
from rich.text import Text
from datetime import datetime
from textual import on

class ListLaunch(Static):
    def compose(self):
        with VerticalScroll():
            with HorizontalScroll(classes="filters"):
                    yield Input(placeholder="***", max_length=3, type="integer", id="bankFilter", classes="inputfilters")
                    yield Input(placeholder="**", max_length=2, type="integer", id="agencyFilter", classes="inputfilters")
                    yield Input(placeholder="*****", max_length=10, type="integer", id="numberFilter", classes="inputfilters")
                    yield Input(placeholder="**", max_length=2, type="text", id="typFilter", classes="inputfilters")
                    yield Input(placeholder="L/N", max_length=1, type="text", id="sitFilter", classes="inputfilters") 
                    yield Input(placeholder="S/N", max_length=1, type="text", id="ticFilter", classes="inputfilters")  
                    yield Input(placeholder="> **_***.**", max_length=33, type="text", id="valueFilter", classes="inputfilters")
                    yield Input(placeholder="> **/**/**", max_length=33, type="text", id="mvDateFilter", classes="inputfilters")
                    yield Input(placeholder="> **/**/**", max_length=33, type="text", id="emDateFilter", classes="inputfilters")
                    yield Button("[red bold] X [/] ", id="clearFilters", classes="hidden")
            yield DataTable(id="ListLaunchTable")


    def _on_mount(self, event):
        self.sortAscending = True
        self.sortColumn = None
        self.table = self.app.query_one("#ListLaunchTable")
        self.table.border_title = "Lista de lançamentos"
        self.table.add_column(Text("Banco", style="bold", justify="center"), key="bank")
        self.table.add_column(Text("+", style="yellow"), key="sep1", width=1)
        self.table.add_column(Text("Agência", style="bold", justify="center"), key="agency")
        self.table.add_column(Text("+", style="yellow"), key="sep2", width=1)
        self.table.add_column(Text("Número", style="bold", justify="center"), key="number")
        self.table.add_column(Text("+", style="yellow"), key="sep3", width=1)
        self.table.add_column(Text("Tipo", style="bold", justify="center"), key="typ")
        self.table.add_column(Text("+", style="yellow"), key="sep4", width=1)
        self.table.add_column(Text("Histórico", style="bold", justify="center"), key="history")
        self.table.add_column(Text("+", style="yellow"), key="sep5", width=1)
        self.table.add_column(Text("Situação", style="bold", justify="center"), key="sit")
        self.table.add_column(Text("+", style="yellow"), key="sep6", width=1)
        self.table.add_column(Text("Ticado", style="bold", justify="center"), key="tic")
        self.table.add_column(Text("+", style="yellow"), key="sep7", width=1)
        self.table.add_column(Text("Valor (R$)", style="bold", justify="center"), key="value")
        self.table.add_column(Text("+", style="yellow"), key="sep8", width=1)
        self.table.add_column(Text("Data do movimento", style="bold", justify="center"), key="movdate")
        self.table.add_column(Text("+", style="yellow"), key="sep9", width=1)
        self.table.add_column(Text("Data de emissão", style="bold", justify="center"), key="emdate")

        self.app.query_one(".filters").border_title = "Filtros"
        self.app.query_one("#bankFilter").border_title = "Banco"
        self.app.query_one("#agencyFilter").border_title = "Ag"
        self.app.query_one("#valueFilter").border_title = "Valor"
        self.app.query_one("#typFilter").border_title = "Tipo"
        self.app.query_one("#numberFilter").border_title = "Número"
        self.app.query_one("#sitFilter").border_title = "Sit"
        self.app.query_one("#ticFilter").border_title = "Tic"
        self.app.query_one("#mvDateFilter").border_title = "Data do movimento"
        self.app.query_one("#emDateFilter").border_title = "Data de emissão"

        self.clearButton = self.app.query_one("#clearFilters")
        self.clearButton.display = "none"
        self.refreshTable()
        return super()._on_mount(event)

    def refreshTable(self, launches=None):
        self.table.clear()
        self.table.loading = True
        launches = launches if launches is not None else self.app.LAUNCH.getAllLaunches()

        if self.sortColumn is not None:
            launches.sort(key=lambda x: x[self.sortColumn], reverse=not self.sortAscending)

        if not launches:    
            self.table.add_row(
                Text(f"***", style="bold", justify="center"), Text("+", style="bold yellow"),
                Text(f"**", style="bold", justify="center"), Text("+", style="bold yellow"),
                Text(f" - ", style="bold", justify="center"), Text("+", style="bold yellow"),
                Text(f"**", justify="center"), Text("+", style="bold yellow"),
                Text(f" - ", justify="center"), Text("+", style="bold yellow"),
                Text(f" - ", justify="center"), Text("+", style="bold yellow"),
                Text(f" - ", justify="center"), Text("+", style="bold yellow"),
                Text(f" - ", style="bold", justify="left"), Text("+", style="bold yellow"),
                Text(f"**/**/**", justify="center"), Text("+", style="bold yellow"),
                Text(f"**/**/**", justify="center"),
            )

        for launch in launches:
            idd, bank, agency, typ, number, valueIntPart, valueDecimalPart, history, sit, checked, movimentDay, movimentMonth, movimentYear, emissionDay, emissionMonth, emissionYear = launch
            value = f"{str(f"{valueIntPart:,}").replace(",", ".")},{valueDecimalPart:02d}"
            sit = ("Lançado", "green") if sit == 1 else ("Não lançado", "red")
            ticado = ("*", "green") if checked == 1 else ("-", "red")

            self.table.add_row(
                Text(f"{str(bank).zfill(3)}", style="bold", justify="center"), Text("|", style="bold yellow"),
                Text(f"{str(agency).zfill(2)}", style="bold", justify="center"), Text("|", style="bold yellow"),
                Text(f"{number}", style="bold", justify="left"), Text("|", style="bold yellow"),
                Text(f"{typ}", justify="center"), Text("|", style="bold yellow"),
                Text(f"{history}", justify="left"), Text("|", style="bold yellow"),
                Text(f"{sit[0]}", style=f"{sit[1]}", justify="center"), Text("|", style="bold yellow"),
                Text(f"{ticado[0]}", style=f"{ticado[1]}", justify="center"), Text("|", style="bold yellow"),
                Text(f"{value}", style="bold", justify="right"), Text("|", style="bold yellow"),
                Text(f"{str(movimentDay).zfill(2)}/{str(movimentMonth).zfill(2)}/{str(movimentYear)[2:]}", justify="center"), Text("|", style="bold yellow"),
                Text(f"{str(emissionDay).zfill(2)}/{str(emissionMonth).zfill(2)}/{str(emissionYear)}", justify="center"),
                key=f"l{idd}"
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

    @on(Input.Submitted, ".inputfilters")
    def filterSubmitted(self):
        bank = self.app.query_one("#bankFilter").value.strip()
        agency = self.app.query_one("#agencyFilter").value.strip()
        number = self.app.query_one("#numberFilter").value.strip()
        typ = self.app.query_one("#typFilter").value.strip()
        value = self.parseValueFilter(self.app.query_one("#valueFilter").value.strip())
        emdate = self.parseDateFilter(self.app.query_one("#emDateFilter").value.strip())
        mvdate = self.parseDateFilter(self.app.query_one("#mvDateFilter").value.strip())

        sitFilter = self.app.query_one("#sitFilter").value.strip().upper()
        ticFilter = self.app.query_one("#ticFilter").value.strip().upper()

        sit = True if sitFilter == "L" else False if sitFilter == "N" else ""
        tic = True if ticFilter == "S" else False if ticFilter == "N" else ""

        if bank and not self.validateFilterBank(bank): 
            self.app.notify("Banco deve ter 3 dígitos numéricos.", severity="error")
            return
        if agency and not self.validateFilterAgency(agency):
            self.app.notify("Agência deve ter 2 dígitos numéricos.", severity="error")
            return
        if number and not self.validateFilterNumber(number):
            self.app.notify("Número deve ser um inteiro válido.", severity="error")
            return
        if typ and not self.validateFilterType(typ):
            self.app.notify("Tipo deve ter até 2 caracteres.", severity="error")
            return
        if value and not self.validateFilterValue(value):
            self.app.notify("Valor deve estar no formato '[X] **_***.**', onde X é ou > ou < e marca a condição", severity="error")
            return
        if emdate and not self.validateFilterDate(emdate):
            self.app.notify("Data de emissão deve estar no formato DD/MM/YY.", severity="error")
            return
        if mvdate and not self.validateFilterDate(mvdate):
            self.app.notify("Data de movimento deve estar no formato DD/MM/YY.", severity="error")
            return

        launches = self.app.LAUNCH.filterLaunch(bank, agency, number, value, typ, emdate, mvdate, sit, tic)
        self.clearButton = self.app.query_one("#clearFilters")
        self.clearButton.display = "block"
        self.refreshTable(launches)

    def parseValueFilter(self, value):
        """Converte o valor do filtro para um formato adequado para a consulta."""
        if not value:
            return []
        if value.startswith(">") or value.startswith("<"):
            return [value[0], value[1:].strip()]
        return [value.strip()]

    def parseDateFilter(self, date):
        """Converte a data do filtro para um formato adequado para a consulta."""
        if not date:
            return []
        if date.startswith(">") or date.startswith("<"):
            return [date[0], date[1:].strip()]
        return [date.strip()]

    def validateFilterBank(self, bank):
        return bank.isdigit() and len(bank) == 3

    def validateFilterAgency(self, agency):
        return agency.isdigit() and len(agency) == 2

    def validateFilterNumber(self, number):
        return number.isdigit()

    def validateFilterType(self, typ):
        return len(typ) <= 2

    def validateFilterValue(self, value):
        if len(value) == 2:
            return len(value[1]) <= 33 and value[0] in ("<", ">") and value[1].replace(",", "").replace(".", "").replace("-", "").isdigit()
        
        return len(value[0]) <= 33 and value[0].replace(",", "").replace(".", "").replace("-", "").isdigit()

    def validateFilterDate(self, date):
        try:
            if len(date) == 2:
                datetime.strptime(date[1] if isinstance(date, list) else date, "%d/%m/%y")
                return date[0] in ("<", ">")
            
            datetime.strptime(date[0] if isinstance(date, list) else date, "%d/%m/%y")
            return True
        except:
            return False

    @on(Button.Pressed, "#clearFilters")
    def clearFilters(self, event):
        self.app.query_one("#bankFilter").value = ""
        self.app.query_one("#agencyFilter").value = ""
        self.app.query_one("#numberFilter").value = ""
        self.app.query_one("#typFilter").value = ""
        self.app.query_one("#valueFilter").value = ""
        self.app.query_one("#emDateFilter").value = ""
        self.app.query_one("#mvDateFilter").value = ""
        self.app.query_one("#sitFilter").value = ""
        self.app.query_one("#ticFilter").value = ""

        self.clearButton = self.app.query_one("#clearFilters")
        self.clearButton.display = "none"
        self.refreshTable()

    def _on_screen_resume(self):
        self.refreshTable()
        return super()._on_screen_resume()