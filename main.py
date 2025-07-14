from textual.app import App, SystemCommand
from textual.widgets import Header, Footer, Button, Label
from textual.containers import Grid, Vertical
from textual.screen import Screen
from textual import on
from rich.text import Text

from screens.AccountScreen import AccountScreen
from screens.HistoryScreen import HistoryScreen
from screens.RelatoryScreen import RelatoryScreen
from screens.LaunchScreen import LaunchScreen
from screens.LoadingScreen import LoadingScreen
from screens.ExitScreen import ExitScreen
from screens.RemoveAccountScreen import RemoveAccountScreen
from screens.RemoveLaunchScreen import RemoveLaunchScreen
from models.DataBaseManager import DatabaseManager
from models.Account import Account
from models.Launch import Launch



class BankControlApp(App):
    TITLE = "Controle bancário"
    COMMAND_PALETTE_BINDING = "ctrl+a"
    CSS_PATH = [
        "styles/styles.tcss", 
        "styles/account.tcss",
        "styles/launch.tcss"
    ]
    BINDINGS = [
        ("ctrl+s", "app.push_screen('ExitScreen')", "Sair"),
        ("ctrl+a", "app.action_command_palette()", "Trocar de tela"),
    ]
    SCREENS = {
        "AccountScreen": AccountScreen,
        "LaunchScreen": LaunchScreen,
        "RelatoryScreen": RelatoryScreen,
        "HistoryScreen": HistoryScreen,
        "LoadingScreen": LoadingScreen,
        "ExitScreen": ExitScreen,
        "RemoveAccountScreen": RemoveAccountScreen,
        "RemoveLaunchScreen": RemoveLaunchScreen,
    }

    DB: DatabaseManager|None = None
    ACCOUNT: Account|None = None
    LAUNCH: Launch|None = None

    def compose(self):
        yield Header(show_clock=True, icon=":bank:")
        with Vertical(classes="nav-menu"):
            with Grid(classes="side-bar-grid"):
                yield Button("[ :dollar_banknote: ] Contas", id="AccountScreen", classes="side-bar-button nav")
                yield Button("[ :bookmark_tabs: ] Históricos", id="HistoryScreen", classes="side-bar-button nav")
                yield Button("[ :book: ] Relatórios", id="RelatoryScreen", classes="side-bar-button nav")
                yield Button("[ :money_bag: ] Lançamentos", id="LaunchScreen", classes="side-bar-button nav")
        yield Label("Julio C. Moreira - 2025", id="author")
        yield Footer()

    def on_mount(self):
        self.app.push_screen("LoadingScreen")

        self.DB = DatabaseManager()
        self.ACCOUNT = Account(self.app.DB)
        self.LAUNCH: Launch = Launch(self.DB)
        self.LAUNCH_NUMBERS = list(map(lambda x: (str(x[0]).zfill(3), str(x[1]).zfill(2), str(x[2])), self.app.LAUNCH.getNumbersBanksAgencys()))
        self.NUMBERS = list(map(lambda x: (str(x[0]).zfill(3), str(x[1]).zfill(2)), self.app.ACCOUNT.getAllBankAndAgency()))
        self.BANK_NUMBERS = [x[0] for x in self.NUMBERS]
        self.AGENCY_NUMBERS = [x[1] for x in self.NUMBERS]

        launchsNotReleased = self.LAUNCH.getAllLaunchNotReleased()
        if launchsNotReleased:
            for launch in launchsNotReleased:
                valueIntPart, valueDecimalPart, bank, agency, number = launch
                value = float(f"{valueIntPart}.{valueDecimalPart}")
                
                self.ACCOUNT.addBalance(bank, agency, value)
                self.LAUNCH.changeSituation(1, number, bank, agency)
                self.notify(f"Lançamento {number} concluído com sucesso")
        
        self.app.pop_screen()
        self.query_one(Grid).border_subtitle = ":money_with_wings:"
        self.query_one(Grid).border_title = "Menu"

    @on(Button.Pressed, ".nav")
    def changeScreen(self, event: Button.Pressed):
        self.push_screen(event.button.id)

    def get_system_commands(self, screen: Screen):
        yield SystemCommand("Contas", "Operações com as contas dos bancos", self._account)
        yield SystemCommand("Históricos", "Em construção", self._history)
        yield SystemCommand("Relatórios", "Em construção", self._relatory)
        yield SystemCommand("Lançamentos", "Operações com os lançamentos", self._launch)

    def _account(self):
        self.push_screen('AccountScreen')
    
    def _relatory(self):
        self.push_screen('RelatoryScreen')
    
    def _history(self):
        self.push_screen('HistoryScreen')

    def _launch(self):
        self.push_screen('LaunchScreen')
        

if __name__ == "__main__":
    # try:
        BankControlApp().run()
    # except:
