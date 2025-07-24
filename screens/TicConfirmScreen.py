from textual.screen import ModalScreen
from textual.widgets import Button, Label, Select
from textual.containers import Vertical, Horizontal

class TicConfirmScreen(ModalScreen):
    BINDINGS = [("escape", "app.pop_screen", "Voltar")]

    def compose(self):
        with Vertical(id="dialogTic"):
            yield Label("O que você quer fazer?", id="confirmMsg")
            yield Select([("Ticar", "T"),("Não ticar", "N"),("Excluir", "D")], allow_blank=False, id="selectTic")
            with Horizontal():
                yield Button("Concluir ação", variant="error", id="concludeTic")
                yield Button("Cancelar", variant="primary", id="cancelTic")


    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "concludeTic":
            self.dismiss(self.app.query_one("#selectTic").value)
        else:
            self.app.pop_screen()
