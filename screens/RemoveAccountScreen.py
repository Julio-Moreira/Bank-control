from textual.screen import ModalScreen
from textual.widgets import Button, Label
from textual.containers import Grid

class RemoveAccountScreen(ModalScreen):
    BINDINGS = [("escape", "app.pop_screen", "Voltar")]

    def compose(self):
        yield Grid(
            Label(f"Tem certeza que quer remover a conta?", id="question"),
            Button("Sim", variant="error", id="yes"),
            Button("Não", variant="primary", id="no"),
            id="dialog",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "yes":
            self.dismiss(True)
        else:
            self.dismiss(False)
