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

        # --- MENU DÉROULANT DU LEADERBOARD (Calque supérieur) ---
        with Vertical(id="leaderboard-dropdown"):
            yield DataTable(id="leaderboard-table")

    def on_mount(self) -> None:
        # self.app.set_focus(None)
        # self.query_one("#system-terminal", Terminal).start()

        editor = self.query_one("#code-input", TextArea)
        editor.indent_width = 4

        table = self.query_one("#leaderboard-table", DataTable)
        table.cursor_type = "row"
        table.add_columns("Rank", "User", "Score")

        console = self.query_one("#console-output")
        # console.write("System initialized. Ready.")

        # --- GÉNÉRATION D'UNE FAUSSE LISTE LONGUE ---
        import random
        
        # Quelques noms de base pour mélanger
        base_names = ["Neo", "Trinity", "Morpheus", "Cypher", "Ghost", "Niobe", "Oracle", "Smith", "Babel", "Root"]
        
        # On génère 100 joueurs fictifs
        for i in range(1, 101):
            # On pioche un nom au hasard et on lui ajoute un suffixe numérique
            username = f"{random.choice(base_names)}_{random.randint(10, 99)}"
            
            # Un score qui diminue pour simuler un classement logique
            score = 10000 - (i * random.randint(10, 80))
            
            # On ajoute la ligne au tableau (les données doivent être des tuples ou listes)
            table.add_row(f"#{i}", username, str(score))
        
        # ---------------------------------------------
        picker = self.query_one("#subject-picker", OptionList)
        picker.add_options(self.mes_challenges)
        self.set_focus(picker)

        self.query_one("#chrono", Label).update("--:--:--")
        
        self.chrono_timer = None
        self.end_time = None
        

        self.set_timer(0.1, self.fade_in_layout)
        # GlitchEffect(self.query_one("#zone-subject"))
        # GlitchEffect(self.query_one("#zone-editor"), 0.2)
        

    def start_server_chrono(self, duration_in_seconds: int) -> None:
        """Déclenché quand le client reçoit le paquet START_CONTEST."""
        # On fixe une heure de fin absolue dans le futur
        self.end_time = datetime.now() + timedelta(seconds=duration_in_seconds)
        
        # On nettoie un éventuel ancien timer
        if self.chrono_timer is not None:
            self.chrono_timer.stop()
            
        # On lance la boucle d'affichage visuel purement locale
        self.chrono_timer = self.set_interval(1.0, self._update_chrono_display)
        self._update_chrono_display() # Force le premier affichage instantané

    def sync_server_chrono(self, seconds_remaining: int) -> None:
        """Déclenché quand le serveur envoie un ping de resynchronisation."""
        # Corrige l'heure de fin si le client a drifté
        self.end_time = datetime.now() + timedelta(seconds=seconds_remaining)

    def stop_server_chrono(self) -> None:
        """Déclenché quand le serveur envoie le paquet END_CONTEST."""
        if self.chrono_timer is not None:
            self.chrono_timer.stop()
        self.query_one("#chrono", Label).update("⏱️ 00:00:00")
        self.end_time = None

    # ========================================================
    # MOTEUR VISUEL LOCAL
    # ========================================================

    def _update_chrono_display(self) -> None:
        """Appelé par Textual chaque seconde pour rafraîchir l'écran."""
        if self.end_time is None:
            return

        # On calcule le temps restant EXACT à cet instant T
        time_left = self.end_time - datetime.now()
        total_seconds = int(time_left.total_seconds())
        
        if total_seconds <= 0:
            self.stop_server_chrono()
            # C'est ici que vous bloquerez l'éditeur de code à la fin !
            return
            
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        time_str = f"⏱️ {hours:02d}:{minutes:02d}:{seconds:02d}"
        self.query_one("#chrono", Label).update(time_str)

    # def on_tabbed_content_tab_activated(self, event: TabbedContent.TabActivated) -> None:
        # if event.pane.id == "tab-terminal":
        #     self.query_one("#system-terminal", BabelExecutor).focus_terminal()
                

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Gère l'affichage/masquage des éléments."""
        if event.button.id == "btn-back":
            # On cache l'éditeur
            self.query_one("#editor-workspace").styles.display = "none"
            # On réaffiche la liste des challenges
            subject_picker = self.query_one("#subject-picker", OptionList)
            # subject_picker.add_options(self.mes_challenges)
            subject_picker.styles.display = "block"
            subject_picker.styles.opacity = 1.0
            self.set_focus(subject_picker)
            
            # On recache le bouton retour
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
            # Si on active l'éditeur, il réapparaît et le sujet reprend sa taille normale (35%)
            if event.value:
                zone_editor.remove_class("collapsed")
                zone_subject.remove_class("maximized")
            # Si on désactive l'éditeur, on le cache et le sujet prend tout l'écran (100%)
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

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        picker = self.query_one("#subject-picker")
        # challenge_id = event.option.id
        
        # self.query_one("#subject-content", Markdown).update(f"# {event.option.prompt}\n\nLoading constraints for {challenge_id}...")
        # self.query_one("#subject-content", Markdown).update(sujet)
        subject_widget = self.query_one("#subject-content", CypherMarkdown)
        subject_widget.decode_text(sujet, duration_sec=1.0)

        # subject_widget.type_text(sujet, 1, 0.02)


        picker.styles.animate(
            attribute="opacity",
            value=0.0,
            duration=0.5,
            on_complete=self.reveal_editor
        )

    def on_option_list_option_highlighted(self, event: OptionList.OptionHighlighted) -> None:
        """Déclenché quand le joueur survole un challenge (prévisualisation)."""
        if event.option is None:
            return
            
        challenge_id = event.option.id or ""
        texte_sujet = FAUX_SUJETS.get(challenge_id, "Sujet introuvable.")
        
        subject_widget = self.query_one("#subject-content", CypherMarkdown)
        subject_widget.decode_text(texte_sujet, duration_sec=0.4)

    def reveal_editor(self) -> None:
        self.query_one("#subject-picker").styles.display = "none"
        self.query_one("#btn-back").styles.display = "block"
        # self.query_one("#code-input").
        self.set_focus(self.query_one("#code-input"))
        

        
        workspace = self.query_one("#editor-workspace")
        workspace.styles.display = "block"
        workspace.styles.animate(
            attribute="opacity",
            value=1.0,
            duration=1.0,
            easing="out_cubic"
        )
