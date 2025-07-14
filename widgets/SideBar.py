from textual.widgets import Static, Label, Button
from textual.containers import Grid, Vertical, Horizontal


class SideBar(Static):
    def compose(self):
        with Horizontal(classes='sidebar-hoz'):
            with Vertical(id="sidebar-first"):
                yield Label(":dollar_banknote:", classes="icon-sidebar")
                yield Label(":money_bag:", classes="icon-sidebar")
                yield Label(":bookmark_tabs:", classes="icon-sidebar")
                yield Label(":book:", classes="icon-sidebar")
                
            with Vertical(id="sidebar-second-nav"):
                yield Button("Contas", id="AccountScreen", classes="button-sidebar nav")
                yield Button("Lançamentos", id="LaunchScreen", classes="button-sidebar nav")
                yield Button("Histórico", id="HistoryScreen", classes="button-sidebar nav")
                yield Button("Relatórios", id="RelatoryScreen", classes="button-sidebar nav")
