from textual import on
from textual.screen import Screen
from textual.widgets import Header, Footer, TabbedContent, TabPane, DataTable, Input, Button
from textual.containers import Horizontal, HorizontalScroll
from textual.suggester import SuggestFromList, SuggestionReady
from rich.text import Text

from widgets.SideBar import SideBar
from widgets.ChangeAccount import ChangeAccount
from widgets.Conference import Conference
from screens.RemoveAccountScreen import RemoveAccountScreen
from datetime import datetime


class AccountScreen(Screen):
    BINDINGS = [
        ("escape", "app.pop_screen", "Voltar"),
    ]

    def compose(self):
        yield Header(show_clock=True, icon=":dollar_banknote:")
        with TabbedContent(id="tabsAccount"):
            with TabPane("Lista"):
                yield DataTable(id="accountTable")
            with TabPane("Inclusão/alteração"):
                yield ChangeAccount()
            with TabPane("Conferência de saldos"):
                yield Conference()
        yield Footer()

    def _on_mount(self, event):
      
        self.editAccount = False
        self.sortAscending = True
        self.sortColumn = None

        self.table = self.app.query_one(DataTable)
        self.table.border_title = "Lista de contas"
        self.table.add_column(Text("Banco", style="bold", justify="center"), key="bank")
        self.table.add_column(Text("+", style="yellow"), key="sep1", width=1)
        self.table.add_column(Text("Agência", style="bold", justify="center"), key="agency")
        self.table.add_column(Text("+", style="yellow"), key="sep2", width=1)
        self.table.add_column(Text("Descrição do Banco", style="bold", justify="center"), key="description")
        self.table.add_column(Text("+", style="yellow"), key="sep3", width=1)
        self.table.add_column(Text("Saldo (R$)", style="bold", justify="center"), key="balance")
        self.table.add_column(Text("+", style="yellow"), key="sep4", width=1)
        self.table.add_column(Text("Data do movimento", style="bold", justify="center"), key="date")

        
        self.app.query_one("#bank").suggester = SuggestFromList(self.app.BANK_NUMBERS)
        self.app.query_one("#agency").suggester = SuggestFromList(self.app.AGENCY_NUMBERS)

        self.refreshTable() 
        return super()._on_mount(event)

    def refreshTable(self, accounts=None):
        self.table.clear()
        self.table.loading = True
        accounts = accounts if accounts is not None else self.app.ACCOUNT.getAllAccounts()

        if self.sortColumn is not None:
            accounts.sort(key=lambda x: x[self.sortColumn], reverse=not self.sortAscending)

        if not accounts:
            self.table.add_row(
                Text("***", style="bold", justify="center"), Text("+", style="bold yellow"),
                Text("**", style="bold", justify="center"), Text("+", style="bold yellow"),
                Text(" - ", justify="center"), Text("+", style="bold yellow"),
                Text(f"R$ **,***.**", style="bold", justify="left"), Text("+", style="bold yellow"),
                Text("**/**/**", justify="center")
            )

        for account in accounts:
            _, bank, agency, name, balanceIntPart, balanceDecimalPart, day, mouth, year = account
            bank = str(bank).zfill(3)
            agency = str(agency).zfill(2)
            balance = f"{str(f"{balanceIntPart:,}").replace(",", ".")},{balanceDecimalPart:02d}"

            self.table.add_row(
                Text(bank, style="bold", justify="center"), Text("│", style="bold yellow"),
                Text(agency, style="bold", justify="center"), Text("│", style="bold yellow"),
                Text(name, justify="left"), Text("│", style="bold yellow"),
                Text(f"{balance}", style="bold", justify="right"), Text("│", style="bold yellow"),
                Text(f"{str(day).zfill(2)}/{str(mouth).zfill(2)}/{str(year)[2:]}", justify="center"),
                key=f"b{bank}{agency}"
            )
        self.table.loading = False

    @on(DataTable.HeaderSelected)
    def sort_table(self, event):
        column_map = {
            "bank": self.action_sort_by_bank,
            "agency": self.action_sort_by_agency,
            "description": self.action_sort_by_description,
            "balance": self.action_sort_by_balance,
            "date": self.action_sort_by_date,
        }
        if event.column_key in column_map:
            column_map[event.column_key]()

    def toggle_sort(self, key):
        if not hasattr(self, "sort_state"):
            self.sort_state = {}
        self.sort_state[key] = not self.sort_state.get(key, False)
        return self.sort_state[key]

    def action_sort_by_bank(self):
        self.table.sort("bank", key=lambda x: x.plain if isinstance(x, Text) else int(x), reverse=self.toggle_sort("bank"))

    def action_sort_by_agency(self):
        self.table.sort("agency", key=lambda x: x.plain if isinstance(x, Text) else int(x), reverse=self.toggle_sort("agency"))

    def action_sort_by_description(self):
        self.table.sort("description", key=lambda x: x.plain if isinstance(x, Text) else str(x), reverse=self.toggle_sort("description"))

    def action_sort_by_balance(self):
        self.table.sort("balance", key=lambda x: float(str(x.plain).replace(".", "").replace(",", ".")) if isinstance(x, Text) else float(str(x.plain).replace(".", "").replace(",", ".")) , reverse=self.toggle_sort("balance"))

    def action_sort_by_date(self):
        self.table.sort("date", key=lambda x: datetime.strptime(x.plain, "%d/%m/%y") if isinstance(x, Text) else datetime.strptime(str(x), "%d/%m/%y"), reverse=self.toggle_sort("date"))

    @on(Input.Submitted, ".addorremove")
    def submitted(self):
        bank, agency, name, balance = self.getInfo()

        if not self.validateBank(bank): 
            self.app.notify("Campo banco deve ser um número de 3 digitos", severity="error")
            return
        elif not self.validateAgency(agency):
            self.app.notify("Campo agência deve ser um número de 2 digitos", severity="error")
            return
        elif not all([name, balance]): 
            return
        elif not self.validateName(name):
            self.app.notify("Campo descrição deve ter pelo menos 1 caracter", severity="error")
            return
        elif not self.validateBalance(balance):
            self.app.notify("Campo saldo deve ser um número no formato R$ **,***,***.** e deve ter no maximo 32 digitos", severity="error")
            return

        bank = str(bank).zfill(3)
        agency = str(agency).zfill(2)
        date = datetime.today()

        if (bank, agency) in self.app.NUMBERS:
            self.app.ACCOUNT.editAccount(bank, agency, name, balance, date.day, date.month, date.year)
            self.app.notify(f"Conta {bank}-{agency} alterada com sucesso!")
        else:
            self.app.ACCOUNT.addAccount(bank, agency, name, balance, date.day, date.month, date.year)
            self.app.BANK_NUMBERS.append(bank)
            self.app.AGENCY_NUMBERS.append(agency)
            self.app.NUMBERS.append((bank, agency))
            self.app.query_one("#bank").suggester = SuggestFromList(self.app.BANK_NUMBERS)
            self.app.query_one("#agency").suggester = SuggestFromList(self.app.AGENCY_NUMBERS)
            self.app.notify(f"Conta {bank}-{agency} adicionada com sucesso!")

        self.refreshTable()
        self.changeInfo()
        self.changePlaceholder()

    def validateBank(self, bank):
        return bank.isdigit() and len(bank) == 3

    def validateAgency(self, agency):
        return agency.isdigit() and len(agency) > 0

    def validateName(self, name):
        return len(name.strip()) > 0

    def validateBalance(self, balance):
        try:
            float(balance.replace(",", "."))
            if len(str(balance)) <= 32:
                return True
            else:
                return False
        except ValueError:
            return False

    @on(Button.Pressed, "#remove")
    def remove(self, event):
        def confirmRemove(res):
            bank, agency, _, _ = self.getInfo()
            bank = str(bank).zfill(3)
            agency = str(agency).zfill(2)

            if res:
                self.app.ACCOUNT.removeAccount(bank, agency)
                self.table.remove_row(f"b{bank}{agency}")
                self.app.notify(f"Conta {bank}-{agency} removida com sucesso!")
                self.changeInfo()
                self.app.BANK_NUMBERS.remove(bank)
                self.app.AGENCY_NUMBERS.remove(agency)
                self.app.query_one("#bank").suggester = SuggestFromList(self.app.BANK_NUMBERS)
                self.app.query_one("#agency").suggester = SuggestFromList(self.app.AGENCY_NUMBERS)

        self.app.push_screen(RemoveAccountScreen(), confirmRemove)

    @on(Input.Submitted, "#bank")
    def autoComplete(self, event):
        bank = str(event.value).zfill(3)
        agency = str(self.app.query_one("#agency").value).zfill(2)

        if bank in self.app.BANK_NUMBERS and agency in self.app.AGENCY_NUMBERS:
            name, balanceInt, balanceDec, _, _, _ = self.app.ACCOUNT.getAccount(bank, agency)
            balance = f"{balanceInt}.{balanceDec:02d}"

            if self.app.query_one("#remove").display == "none":
                self.app.query_one("#remove").display = "block"
                self.editAccount = True

            self.changeInfo(bank, agency, name, balance)

    @on(Input.Submitted, "#agency")
    def autoCompleteAg(self, event):
        agency = str(event.value).zfill(2)
        bank = str(self.app.query_one("#bank").value).zfill(3)

        if (bank, agency) in self.app.NUMBERS:
            account = self.app.ACCOUNT.getAccount(bank, agency)
            if not account:
                return
            
            name, balanceInt, balanceDec, _, _, _ = account
            balance = f"{balanceInt}.{balanceDec:02d}"

            self.changeInfo(bank, agency, name, balance)

            self.app.query_one("#remove").display = "block"
            self.editAccount = True

    @on(SuggestionReady)
    def autoCompletePlaceholder(self):
        agency = str(self.app.query_one("#agency").value)
        bank = str(self.app.query_one("#bank").value)

        if agency == '' or bank == '':
            return
        
        if (bank.zfill(3), agency.zfill(2)) in self.app.NUMBERS:
            account = self.app.ACCOUNT.getAccount(bank.zfill(3), agency.zfill(2))
            if not account:
                return
            
            name, balanceInt, balanceDec, _, _, _ = account
            balance = f"{balanceInt}.{balanceDec:02d}"

            self.changePlaceholder(bank, agency, name, balance)

    @on(Input.Changed, "#agency")
    def resetPlaceholderAg(self, event: Input.Changed):
        self.changePlaceholder()    
        agency = str(self.app.query_one("#agency").value)
        bank = str(self.app.query_one("#bank").value)

        if self.editAccount and (bank.zfill(3) not in self.app.BANK_NUMBERS or agency.zfill(2) not in self.app.AGENCY_NUMBERS):
            self.changeInfo(agency=event.value, bank=f"{self.app.query_one("#bank").value}")
            self.app.query_one("#remove").display = "none"
            self.editAccount = False

    def getInfo(self):
        return (
            self.app.query_one("#bank").value,
            self.app.query_one("#agency").value,
            self.app.query_one("#name").value,
            str(self.app.query_one("#balance").value),
        )

    def changeInfo(self, bank="", agency="", name="", balance=""):
        self.app.query_one("#bank").value = str(bank)
        self.app.query_one("#agency").value = str(agency)
        self.app.query_one("#name").value = str(name)
        self.app.query_one("#balance").value = str(balance)

    def changePlaceholder(self, bank="***", agency="**", name=":", balance="R$ **_***.**"):
        self.app.query_one("#bank").placeholder = str(bank)
        self.app.query_one("#agency").placeholder = str(agency)
        self.app.query_one("#name").placeholder = str(name)
        self.app.query_one("#balance").placeholder = str(balance)

    def _on_screen_resume(self):
        self.refreshTable()
        return super()._on_screen_resume()
    