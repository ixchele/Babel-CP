from datetime import datetime, timedelta
from textual.app import ComposeResult
import textual.app

from textual.screen import Screen
from textual.containers import Horizontal, Vertical, Center, Middle
from textual.widgets import Input, Label, Markdown, TextArea, RichLog, DataTable, OptionList, TabbedContent, TabPane, Switch
from textual.widgets.option_list import Option

from widgets.effects import GlitchEffect 
from widgets.cutom_widgets import BabelPushTab, BabelTextArea, CypherMarkdown, TypewriterMarkdown, BabelExecutor


FAUX_SUJETS = {
    "chal_1": "# Challenge 01: The Matrix\n\nTrouvez les deux nœuds d'énergie...",
    "chal_2": "# Challenge 02: Babel Syntax\n\nÉcrivez un parseur pour l'EBNF...",
    "chal_3": "# Challenge 03: Memory Leak\n\nDétectez la fuite dans cet allocateur C++98...",
    "chal_4": "# Challenge 04: The Oracle\n\nPrédisez le prochain cycle d'horloge...",
}

sujet = """
# Challenge 01: The Matrix Initialization

## Contexte
Bienvenue dans l'arène du Projet Babel. 

Avant de pouvoir déployer vos algorithmes sur le réseau principal, le serveur d'évaluation requiert une initialisation du noyau de routage. Le système vous fournit un flux d'entiers représentant l'état énergétique des nœuds de communication.

## Mission
Écrivez une fonction qui analyse le flux et identifie les **deux nœuds** dont l'énergie combinée correspond exactement à la `cible` d'activation. 

## Spécifications

**Entrées :**
* `signals` : Une liste d'entiers représentant l'énergie des nœuds (longueur de 2 à 10 000).
* `target` : L'entier cible à atteindre.

**Sortie :**
* Retournez une liste contenant les indices exacts de ces deux nœuds.

## Contraintes
* Complexité temporelle attendue : **O(N)**.
* Complexité spatiale autorisée : **O(N)**.
* Chaque jeu de test possède **exactement une seule solution**.
* Il est interdit d'utiliser la même adresse mémoire (le même nœud) deux fois.

---

## Exemples

### Cas nominal
```python
Entrée : signals = [2, 7, 11, 15], target = 9
Sortie : [0, 1]
Explication : signals[0] + signals[1] == 9, on retourne les indices 0 et 1.
"""


from textual.app import ComposeResult
from textual.screen import Screen
from textual.containers import Horizontal, Vertical
from textual.widgets import Markdown, TextArea, RichLog, DataTable, OptionList, Button
from textual.widgets.option_list import Option

class ArenaScreen(Screen):

    CSS_PATH = "../styles/arena-screen.css"
    AUTO_FOCUS = ""

    mes_challenges = [
        Option("Challenge 01: The Matrix Initialization", id="chal_1"),
        Option("Challenge 02: Babel Syntax Analyzer", id="chal_2"),
        Option("Challenge 03: Memory Leak Hunt", id="chal_3"),
        Option("Challenge 04: The Oracle's Prediction", id="chal_4"),
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db_problems = {}

    def compose(self) -> ComposeResult:
        # --- TOP BAR ---
        with Horizontal(id="top-bar"):
            with Horizontal(id="window-controls-1"):
                yield Switch(name="subject", value=True, id="switch-toggle-subject")
                yield Switch(value=True, id="switch-toggle-editor")
                yield Button("◀ Back", id="btn-back", variant="primary")

            with Center(id="chrono-bar"):
                yield Label("02:00:00", id="chrono")
            
            with Horizontal(id="window-controls-2"):
                yield Button("User: ixchele | Score: 1250 pts | Rank: 1", id="btn-toggle-stats", variant="primary")

        with Horizontal(id="arena-layout"):
            with Vertical(id="zone-subject"):
                yield CypherMarkdown("# Select a challenge...\nWaiting for input.", id="subject-content")
                # yield TypewriterMarkdown(sujet, id="subject-content")
                # yield Markdown("# Select a challenge...\nWaiting for input.", id="subject-content")

            with Vertical(id="zone-editor"):
                yield OptionList(id="subject-picker")
                
                with Vertical(id="editor-workspace"):
                    # yield TextArea(language="python", show_line_numbers=True, tab_behavior="indent", id="code-input")
                    yield BabelTextArea(language="python", show_line_numbers=True, tab_behavior="indent", id="code-input")
                    with TabbedContent(id="bottom-tabs"):

                        with TabPane("TestCase", id="tab-terminal"):
                            yield BabelExecutor(id="system-terminal")

                        with TabPane("Push Solution", id="tab-tests"):
                            yield BabelPushTab(id="push-tab")

                        with TabPane("Traces", id="tab-console"):
                            yield RichLog(id="console-output", highlight=True)

        with Vertical(id="leaderboard-dropdown"):
            yield DataTable(id="leaderboard-table")


    async def on_mount(self) -> None:
        editor = self.query_one("#code-input", TextArea)
        editor.indent_width = 4

        table = self.query_one("#leaderboard-table", DataTable)
        table.cursor_type = "row"
        table.add_columns("Rank", "User", "Score")

        console = self.query_one("#console-output")

        import random
        base_names = ["Neo", "Trinity", "Morpheus", "Cypher", "Ghost", "Niobe", "Oracle", "Smith", "Babel", "Root"]
        for i in range(1, 101):
            username = f"{random.choice(base_names)}_{random.randint(10, 99)}"
            score = 10000 - (i * random.randint(10, 80))
            table.add_row(f"#{i}", username, str(score))

        self.query_one("#chrono", Label).update("--:--:--")
        
        self.chrono_timer = None
        self.end_time = None

        self.set_timer(0.1, self.fade_in_layout)
        
        await self.fetch_and_load_problems()



    def start_server_chrono(self, duration_in_seconds: int) -> None:
        self.end_time = datetime.now() + timedelta(seconds=duration_in_seconds)

        if self.chrono_timer is not None:
            self.chrono_timer.stop()
            
        self.chrono_timer = self.set_interval(1.0, self._update_chrono_display)
        self._update_chrono_display() # Force le premier affichage instantané

    def sync_server_chrono(self, seconds_remaining: int) -> None:
        self.end_time = datetime.now() + timedelta(seconds=seconds_remaining)

    def stop_server_chrono(self) -> None:
        """Déclenché quand le serveur envoie le paquet END_CONTEST."""
        if self.chrono_timer is not None:
            self.chrono_timer.stop()
        self.query_one("#chrono", Label).update("⏱️ 00:00:00")
        self.end_time = None


    def _update_chrono_display(self) -> None:
        if self.end_time is None:
            return

        time_left = self.end_time - datetime.now()
        total_seconds = int(time_left.total_seconds())
        
        if total_seconds <= 0:
            self.stop_server_chrono()
            return
            
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        time_str = f"⏱️ {hours:02d}:{minutes:02d}:{seconds:02d}"
        self.query_one("#chrono", Label).update(time_str)


    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-back":
            self.query_one("#editor-workspace").styles.display = "none"
            subject_picker = self.query_one("#subject-picker", OptionList)
            subject_picker.styles.display = "block"
            subject_picker.styles.opacity = 1.0
            self.set_focus(subject_picker)
            event.button.styles.display = "none"

        if event.button.id == "btn-toggle-subject":
            zone = self.query_one("#zone-subject")
            
            zone.toggle_class("collapsed")
            
            is_collapsed = zone.has_class("collapsed")
            event.button.variant = "default" if is_collapsed else "primary"
            self.set_focus(None)

        elif event.button.id == "btn-toggle-stats":
            dropdown = self.query_one("#leaderboard-dropdown")
            dropdown.toggle_class("expanded")
            is_expanded = dropdown.has_class("expanded")
            event.button.variant = "primary" if is_expanded else "default"
            self.query_one("#leaderboard-table").focus()

    def on_switch_changed(self, event: Switch.Changed) -> None:
        """Déclenché quand l'utilisateur clique sur un Switch."""
        
        zone_subject = self.query_one("#zone-subject")
        zone_editor = self.query_one("#zone-editor")
        
        if event.switch.id == "switch-toggle-subject":
            if event.value:
                zone_subject.remove_class("collapsed")
            else:
                zone_subject.add_class("collapsed")
                
        elif event.switch.id == "switch-toggle-editor":
            if event.value:
                zone_editor.remove_class("collapsed")
                zone_subject.remove_class("maximized")
            else:
                zone_editor.add_class("collapsed")
                zone_subject.add_class("maximized")

    def fade_in_layout(self) -> None:
        layout = self.query_one("#arena-layout", Horizontal)
        layout.styles.animate(
            attribute="opacity",
            value=1.0,
            duration=1.5,
            easing="out_cubic"
        )

    async def fetch_and_load_problems(self) -> None:
        picker = self.query_one("#subject-picker", OptionList)
        picker.clear_options()
        
        try:
            problems = await self.app.api_client.get_problems()
            for p in problems:
                opt_id = f"chal_{p['id']}"
                self.db_problems[opt_id] = p
                
                label = f"󰘨 {p['title']} [{p['difficulty']}]"
                picker.add_option(Option(label, id=opt_id))
                
            self.set_focus(picker)
            
        except Exception as e:
            self.app.log.error(f"Failed to fetch problems: {e}")
            picker.add_option(Option(f"󰚌 API Error: {str(e)}...", id="error"))

    def on_option_list_option_highlighted(self, event: OptionList.OptionHighlighted) -> None:
        if event.option is None or event.option.id == "error":
            return
            
        challenge_id = event.option.id
        problem_data = self.db_problems.get(challenge_id)
        
        if problem_data:
            texte_sujet = f"# {problem_data['title']}\n\n{problem_data['description']}"
        else:
            texte_sujet = "󰚌 Missing data in local cache."
            
        subject_widget = self.query_one("#subject-content", CypherMarkdown)
        subject_widget.decode_text(texte_sujet, duration_sec=0.4)

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        if event.option.id == "error":
            return
            
        picker = self.query_one("#subject-picker")
        
        challenge_id = event.option.id
        problem_data = self.db_problems.get(challenge_id)
        
        if problem_data:
            texte_sujet = f"# {problem_data['title']}\n\n{problem_data['subject']}"
            subject_widget = self.query_one("#subject-content", CypherMarkdown)
            subject_widget.decode_text(texte_sujet, duration_sec=1.0)

        picker.styles.animate(
            attribute="opacity",
            value=0.0,
            duration=0.5,
            on_complete=self.reveal_editor
        )

    def reveal_editor(self) -> None:
        self.query_one("#subject-picker").styles.display = "none"
        self.query_one("#btn-back").styles.display = "block"
        self.set_focus(self.query_one("#code-input"))
        

        
        workspace = self.query_one("#editor-workspace")
        workspace.styles.display = "block"
        workspace.styles.animate(
            attribute="opacity",
            value=1.0,
            duration=1.0,
            easing="out_cubic"
        )
