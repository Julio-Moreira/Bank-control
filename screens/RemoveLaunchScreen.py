from textual.screen import ModalScreen
from textual.widgets import Button, Label
from textual.containers import Grid

class RemoveLaunchScreen(ModalScreen):
    BINDINGS = [("escape", "app.pop_screen", "Voltar")]

    def compose(self):
        yield Grid(
            Label(f"Tem certeza que quer remover o lançamento?", id="questionl"),
            Button("Sim", variant="error", id="yesl"),
            Button("Não", variant="primary", id="nol"),
            id="dialogl",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "yesl":
            self.dismiss(True)
        else:
            self.dismiss(False)
