from textual import on
from textual.widgets import Static, Input, Checkbox, Label, Button
from textual.containers import HorizontalScroll, Vertical
from textual.suggester import SuggestFromList, SuggestionReady
from widgets.Launch.listLaunch import ListLaunch
from screens.RemoveLaunchScreen import RemoveLaunchScreen

from datetime import datetime

class ChangeLaunch(Static):
    def compose(self):
        with Vertical(classes="addLaunch"):
            with HorizontalScroll(classes="lineOneChanged"):
                yield Input(placeholder="***", max_length=3, type="integer", id="bankChange", classes="idents")
                yield Input(placeholder="**", max_length=2, type="integer", id="agencyChange", classes="idents")
                yield Label(" ")
                yield Input(placeholder="**", max_length=2, type="text", id="typeChange")
                yield Input(placeholder="R$ **_***.**", max_length=32, type="number", id="valueChange")
                yield Checkbox(id="checkChange")
            with HorizontalScroll(classes="lineTwoChanged"):
                yield Input(placeholder="****", max_length=10, type="integer", id="numberChange", classes="idents")
                yield Label(" ")
                yield Input(placeholder=":", type="text", max_length=30, id="historyChange")
                yield Input(placeholder="**/**/**", max_length=8, type="text", id="emissionDateChange")
            with HorizontalScroll(classes="lineTreeChanged"):
                yield Button("[red bold] X [/]", id="removeLaunch")


    def _on_mount(self):
        bank = self.app.query_one("#bankChange")
        agency = self.app.query_one("#agencyChange")
        check = self.app.query_one("#checkChange")
        typeLn = self.app.query_one("#typeChange")
        number = self.app.query_one("#numberChange")
        value = self.app.query_one("#valueChange")
        history = self.app.query_one("#historyChange")
        emissionDate = self.app.query_one("#emissionDateChange")
        remove = self.app.query_one("#removeLaunch")

        bank.border_title = "Banco"
        agency.border_title = "Ag"
        check.border_title = ":heavy_check_mark:"
        typeLn.border_title = "Tp"
        number.border_title = "Número"
        value.border_title = "Valor"
        history.border_title = "Histórico"
        emissionDate.border_title = "Data de emissão"

        bank.suggester = SuggestFromList(self.app.BANK_NUMBERS)
        agency.suggester = SuggestFromList(self.app.AGENCY_NUMBERS)
        number.suggester = SuggestFromList(list(map(lambda x: x[2], self.app.LAUNCH_NUMBERS)))
        remove.display = "none"
        self.changed = False

    @on(Input.Submitted)
    def change(self):
        bank, agency, check, typ, number, value, history, emissionDate = self.getInfo()
        IsChecked = 1 if check == True else 0

        if not self.validateBank(bank): 
            self.app.notify("Campo banco deve ser um número de 3 digitos", severity="error")
            return
        elif not self.validateAgency(agency):
            self.app.notify("Campo agência deve ser um número de 2 digitos", severity="error")
            return
        elif not self.validateNumber(number):
            self.app.notify("Campo número deve ter pelo menos 1 caracter", severity="error")
            return
        elif (bank, agency, number) not in self.app.LAUNCH_NUMBERS:
            self.app.notify("Não existe lançamento associado a esse banco, número e agência.", severity="error")
            return
        elif not all([typ, value, history, emissionDate]):
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

        bank = str(bank).zfill(3)
        agency = str(agency).zfill(2)
        emissionDay, emissionMonth, emissionYear = str(emissionDate).split("/")

        emissionDay = str(emissionDay).zfill(2)
        emissionMonth = str(emissionMonth).zfill(2)

        situation, oldValueInt, oldValueDecimal = self.app.LAUNCH.getSituationAndValue(bank, agency, number)
        oldValue = float(f"{oldValueInt}.{oldValueDecimal}")

        if situation == 1:
            self.app.ACCOUNT.addBalance(bank, agency, oldValue * (-1))

            if (str(datetime.today().day).zfill(2) == str(emissionDay).zfill(2)) and (str(datetime.today().month).zfill(2) == str(emissionMonth).zfill(2)) and (str(datetime.today().day)[2:] == str(emissionYear).zfill(2)):
                self.app.ACCOUNT.addBalance(bank, agency, value)

            currentDay = datetime.now().day
            currentMonth = datetime.now().month
            currentYear = datetime.now().year % 100
            if int(emissionYear) > currentYear or (int(emissionYear) == currentYear and (int(emissionMonth) > currentMonth or (int(emissionMonth) == currentMonth and int(emissionDay) > currentDay))):
                situation = 0

        self.app.LAUNCH.editLaunch(bank, agency, typ, number, value, history, IsChecked, situation, emissionDay, emissionMonth, emissionYear)
        self.app.notify(f"Lançamento {number} alterado com sucesso")

        self.app.query_one(ListLaunch).refreshTable()
        self.changeInfo()
        self.changePlaceholder()

    @on(Input.Submitted, ".idents")
    def autoCompleteValues(self):
        bank = str(self.app.query_one("#bankChange").value)
        agency = str(self.app.query_one("#agencyChange").value)
        number = str(self.app.query_one("#numberChange").value)
        if (bank == '') or (agency == '') or (number == ''):
            return
        
        bank = bank.zfill(3)
        agency = agency.zfill(2)

        if (bank, agency, number) in self.app.LAUNCH_NUMBERS:
            launch = self.app.LAUNCH.getLaunch(int(number), agency, bank)
            if launch == [''] * 8:
                return
            
            Typ, ValueIntPart, ValueDecimalPart, History, IsChecked, EmissionDay, EmissionMonth, EmissionYear = launch
            value = f"{ValueIntPart}.{str(ValueDecimalPart).zfill(2)}"
            IsChecked = True if IsChecked == 1 else False

            self.changed = True

            self.changeInfo(bank, agency, IsChecked, Typ, number, value, History, f"{EmissionDay}/{EmissionMonth}/{EmissionYear}")
    
    @on(SuggestionReady)
    def autoCompletePlaceholder(self):
        bank = str(self.app.query_one("#bankChange").value)
        agency = str(self.app.query_one("#agencyChange").value)
        number = str(self.app.query_one("#numberChange").value)

        if (bank == "") or (agency == '') or (number == ''):
            return
        
        bank = bank.zfill(3)
        agency = agency.zfill(2)

        if (bank, agency, number) in self.app.LAUNCH_NUMBERS:
            launch = self.app.LAUNCH.getLaunch(int(number), agency, bank)
            if launch == [''] * 8:
                return
            
            Typ, ValueIntPart, ValueDecimalPart, History, _, EmissionDay, EmissionMonth, EmissionYear = launch
            value = f"{ValueIntPart}.{str(ValueDecimalPart).zfill(2)}"

            self.changePlaceholder(Typ, value, History, f"{EmissionDay}/{EmissionMonth}/{EmissionYear}")
            self.app.query_one("#removeLaunch").display = "block"
    
    @on(Input.Changed, ".idents")
    def resetValues(self):
        bank = str(self.app.query_one("#bankChange").value)
        agency = str(self.app.query_one("#agencyChange").value)
        number = str(self.app.query_one("#numberChange").value)
        self.changePlaceholder()    
        self.app.query_one("#removeLaunch").display = "none"

        if self.changed:
            self.changeInfo(agency=f"{agency}", bank=f"{bank}", number=f"{number}")
            self.changed = False

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
            datetime.strptime(date, "%d/%m/%y")
            return True
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
            self.app.query_one("#bankChange").value,
            self.app.query_one("#agencyChange").value,
            self.app.query_one("#checkChange").value,
            self.app.query_one("#typeChange").value,
            self.app.query_one("#numberChange").value,
            self.app.query_one("#valueChange").value,
            self.app.query_one("#historyChange").value,
            self.app.query_one("#emissionDateChange").value
        )
    
    @on(Button.Pressed, "#removeLaunch")
    def remove(self):
        def confirmRemove(res):
            if not res:
                return
            
            bank, agency, _, _, number, _, _, _ = self.getInfo()
            bank = str(bank).zfill(3)
            agency = str(agency).zfill(2)

            situation, oldValueInt, oldValueDecimal = self.app.LAUNCH.getSituationAndValue(bank, agency, number)
            oldValue = float(f"{oldValueInt}.{oldValueDecimal}")

            if situation == 1:
                self.app.ACCOUNT.addBalance(bank, agency, oldValue * (-1))

            self.app.LAUNCH.removeLaunch(number, bank, agency)
            self.app.notify(f"Lançamento {number} removido com sucesso")
            self.changeInfo()
            self.app.query_one(ListLaunch).refreshTable()
            self.app.LAUNCH_NUMBERS.remove((bank, agency, number))

        self.app.push_screen(RemoveLaunchScreen(), confirmRemove)

    def changeInfo(self, bank = "", agency="", check = "", typ = "", number = "", value = "", history = "", emissionDate = ""):
        self.app.query_one("#bankChange").value = bank
        self.app.query_one("#agencyChange").value = agency
        self.app.query_one("#checkChange").value = check
        self.app.query_one("#typeChange").value = typ
        self.app.query_one("#numberChange").value = number
        self.app.query_one("#valueChange").value = value
        self.app.query_one("#historyChange").value = history
        self.app.query_one("#emissionDateChange").value = emissionDate

    def changePlaceholder(self, typ="**", value="R$ **_***.**", history=": ", emissionDate="**/**/**"):
        self.app.query_one("#typeChange").placeholder = typ
        self.app.query_one("#valueChange").placeholder = value
        self.app.query_one("#historyChange").placeholder = history
        self.app.query_one("#emissionDateChange").placeholder = emissionDate

    # def _on_screen_resume(self):
    #     self.app.query_one("#bankChange").suggester = SuggestFromList(self.app.BANK_NUMBERS)
    #     self.app.query_one("#agencyChange").suggester = SuggestFromList(self.app.AGENCY_NUMBERS)
    #     self.app.query_one("#numberChange").suggester = SuggestFromList(list(map(lambda x: x[2], self.app.LAUNCH_NUMBERS)))
    #     return super()._on_screen_resume()
