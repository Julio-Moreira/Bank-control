from textual import on
from textual.screen import Screen
from textual.widgets import Header, Footer, TabbedContent, TabPane
from textual.containers import Horizontal
from widgets.Launch.includeLaunch import IncludeLaunch
from textual.message import Message


from widgets.SideBar import SideBar
import widgets.Launch.changeLaunch, widgets.Launch.includeLaunch, widgets.Launch.listLaunch, widgets.Launch.ticLaunch

class LaunchScreen(Screen):
    BINDINGS = [
        ('escape', 'app.pop_screen', "Voltar"),
    ]

    def compose(self):
        yield Header(show_clock=True, icon=":money_bag:")
        with TabbedContent(id="tabsAccount"):
            with TabPane("Lista"):
                yield widgets.Launch.listLaunch.ListLaunch()              
            with TabPane("Inclusão"):
                yield  widgets.Launch.includeLaunch.IncludeLaunch()
            with TabPane("Alteração"):
                yield widgets.Launch.changeLaunch.ChangeLaunch()
            with TabPane("Ações"):
                yield widgets.Launch.ticLaunch.TicLaunch()
        yield Footer()
