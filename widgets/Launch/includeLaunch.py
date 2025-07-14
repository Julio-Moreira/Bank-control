from textual import on
from textual.widgets import Static, Input, Checkbox, Label
from textual.containers import HorizontalScroll, Vertical
from textual.suggester import SuggestFromList
from widgets.Launch.listLaunch import ListLaunch
from screens.AccountScreen import AccountScreen

from datetime import datetime


class IncludeLaunch(Static):
    def compose(self):
        with Vertical(classes="addLaunch"):
            with HorizontalScroll(classes="lineOne"):
                yield Input(placeholder="***", max_length=3, type="integer", id="bank")
                yield Input(placeholder="**", max_length=2, type="integer", id="agencyLn")
                yield Label(" ")
                yield Input(placeholder="**", max_length=2, type="text", id="type")
                yield Input(placeholder="R$ **_***.**", max_length=32, type="number", id="value")
            with HorizontalScroll(classes="lineTwo"):
                yield Input(placeholder="****", max_length=10, type="integer", id="number")
                yield Label(" ")
                yield Input(placeholder=":", type="text", max_length=30, id="history")
                yield Input(placeholder="**/**/**", max_length=8, type="text", id="emissionDate")

    def _on_mount(self):
        bank = self.app.query_one("#bank")
        agency = self.app.query_one("#agencyLn")
        typeLn = self.app.query_one("#type")
        number = self.app.query_one("#number")
        value = self.app.query_one("#value")
        history = self.app.query_one("#history")
        emissionDate = self.app.query_one("#emissionDate")

        bank.border_title = "Banco"
        agency.border_title = "Ag"
        typeLn.border_title = "Tp"
        number.border_title = "Número"
        value.border_title = "Valor"
        history.border_title = "Histórico"
        emissionDate.border_title = "Data de emissão"

        bank.suggester = SuggestFromList(self.app.BANK_NUMBERS)
        agency.suggester = SuggestFromList(self.app.AGENCY_NUMBERS)

    @on(Input.Submitted)
    def add(self):
        bank, agency, typ, number, value, history, emissionDate = self.getInfo()

        if not self.validateBank(bank): 
            self.app.notify("Campo banco deve ser um número de 3 digitos", severity="error")
            return
        elif not self.validateAgency(agency):
            self.app.notify("Campo agência deve ser um número de 2 digitos", severity="error")
            return
        
        bank = str(bank).zfill(3)
        agency = str(agency).zfill(2)
        
        if (bank, agency) not in self.app.NUMBERS:
            self.app.notify("Não existe conta associada a esse banco e agência.", severity="error")
            return
        elif not self.validateNumber(number):
            self.app.notify("Campo número deve ser um número com pelo menos 1 caracter", severity="error")
            return
        elif (bank, agency, number) in self.app.LAUNCH_NUMBERS:
            self.app.notify("Esse lançamento já existe", severity="error")
            return
        elif not self.validateType(typ):
            self.app.notify("Campo tipo deve ter pelo menos 1 caracter", severity="error")
            return
        elif not self.validateValue(value):
            self.app.notify("Campo valor deve ser um número no formato R$ [-]**,***,***.** e deve ter no maximo 32 digitos", severity="error")
            return
        elif not self.validateHistory(history):
            self.app.notify("Campo histórico deve ter pelo menos 1 caracter", severity="error")
            return
        elif not self.validateDate(emissionDate):
            self.app.notify("Campo data de emissão deve ser uma data no formato DD/MM/YY", severity="error")
            return

        emissionDay, emissionMonth, emissionYear = str(emissionDate).split("/")

        today = datetime.today()
        movimentDay = today.day
        movimentMonth = today.month
        movimentYear = today.year
        emissionDay = str(emissionDay).zfill(2)
        emissionMonth = str(emissionMonth).zfill(2)
        situation = 0
        IsChecked = 0

        if (str(movimentDay).zfill(2) == str(emissionDay).zfill(2)) and (str(movimentMonth).zfill(2) == str(emissionMonth).zfill(2)) and (str(movimentYear)[2:] == str(emissionYear).zfill(2)):
            situation = 1
            self.app.ACCOUNT.addBalance(bank, agency, value)
            self.app.notify(f"Lançamento concluído com sucesso")
        else:
            self.app.notify(f"Lançamento programado para {emissionDay}/{emissionMonth}/{emissionYear}")

        self.app.LAUNCH.addLaunch(bank, agency, typ, number, value, history, situation, IsChecked,
                  movimentDay, movimentMonth, movimentYear, emissionDay, emissionMonth, emissionYear)

        self.app.query_one(ListLaunch).refreshTable()
        self.app.LAUNCH_NUMBERS.append((bank, agency, number))
        self.changeInfo()
    
    def validateBank(self, bank):
        return bank.isdigit() and len(bank) == 3

    def validateAgency(self, agency):
        return agency.isdigit() and len(agency) > 0

    def validateType(self, typ):
        return len(typ.strip()) > 0
    
    def validateNumber(self, number):
        return number.isdigit() and len(str(number).strip()) > 0

    def validateValue(self, value):
        try:
            float(value)
            if len(str(value)) <= 32:
                return True
            else:
                return False
        except:
            return False
        
    def validateHistory(self, history):
        return len(history.strip()) > 0

    def validateDate(self, date):
        try:
            date_obj = datetime.strptime(date, "%d/%m/%y")
            return date_obj.date() >= datetime.today().date()
        except:
            return False

    @on(Input.Changed, "#emissionDate")
    def dateFormatter(self, event: Input.Changed):
        date_input = self.app.query_one("#emissionDate")
        raw_date = date_input.value.replace("/", "")  

        if len(raw_date) > 2:
            raw_date = raw_date[:2] + "/" + raw_date[2:]
        if len(raw_date) > 5:
            raw_date = raw_date[:5] + "/" + raw_date[5:]
            

        date_input.cursor_position += 1
        date_input.value = raw_date[:8]

    def getInfo(self):
        return (
            self.app.query_one("#bank").value,
            self.app.query_one("#agencyLn").value,
            self.app.query_one("#type").value,
            self.app.query_one("#number").value,
            self.app.query_one("#value").value,
            self.app.query_one("#history").value,
            self.app.query_one("#emissionDate").value
        )
    
    def changeInfo(self, bank = "", agency="", typ = "", number = "", value = "", history = "", emissionDate = ""):
        self.app.query_one("#bank").value = bank
        self.app.query_one("#agencyLn").value = agency
        self.app.query_one("#type").value = typ
        self.app.query_one("#number").value = number
        self.app.query_one("#value").value = value
        self.app.query_one("#history").value = history
        self.app.query_one("#emissionDate").value = emissionDate