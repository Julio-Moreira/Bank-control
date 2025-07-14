from textual.screen import ModalScreen
from textual.widgets import Button, Label
from textual.containers import Grid

class ExitScreen(ModalScreen):
    BINDINGS = [("escape", "app.pop_screen", "Voltar")]

    def compose(self):
        yield Grid(
            Label("Tem certeza que quer sair?", id="question"),
            Button("Sair", variant="error", id="quit"),
            Button("Cancelar", variant="primary", id="cancel"),
            id="dialog",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "quit":
            self.app.exit()
        else:
            self.app.pop_screen()
