import random
from textual.widgets import Markdown, TextArea, Select
from widgets.effects import GlitchEffect

class TypewriterMarkdown(Markdown):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._typewriter_timer = None
        self._full_text = ""
        self._current_index = 0
        self._base_chunk = 15

    def type_text(self, text: str, duration_sec: float = 1.2, interval: float = 0.06) -> None:
        if self._typewriter_timer is not None:
            self._typewriter_timer.stop()
            
        self._full_text = text
        self._current_index = 0
        self.update("") 
        
        total_steps = max(1, duration_sec / interval)
        self._base_chunk = max(1, int(len(text) / total_steps))
        
        self._typewriter_timer = self.set_interval(interval, self._type_next_chunk)

    def _type_next_chunk(self) -> None:
        variation = random.randint(max(1, int(self._base_chunk * 0.8)), int(self._base_chunk * 1.5))
        self._current_index += variation
        
        if self._current_index >= len(self._full_text):
            self._current_index = len(self._full_text)
            if self._typewriter_timer is not None:
                self._typewriter_timer.stop()
                
        self.update(self._full_text[:self._current_index])

import random
import string
from textual.widgets import Markdown

class CypherMarkdown(Markdown):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._cypher_timer = None
        self._full_text = ""
        self._reveal_index = 0
        self._step = 15
        self._matrix_chars = string.ascii_letters + "ｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓﾔﾕﾖﾗﾘﾙﾚﾛﾜﾝ0123456789!@#$%^&*"

    def decode_text(self, text: str, duration_sec: float = 1.0, interval: float = 0.05) -> None:
        if self._cypher_timer is not None:
            self._cypher_timer.stop()
            
        self._full_text = text
        self._reveal_index = 0
        
        total_steps = max(1, duration_sec / interval)
        self._step = max(1, int(len(text) / total_steps))
        
        self._cypher_timer = self.set_interval(interval, self._cypher_tick)

    def _cypher_tick(self) -> None:
        self._reveal_index += self._step
        
        if self._reveal_index >= len(self._full_text):
            self.update(self._full_text)
            if self._cypher_timer is not None:
                self._cypher_timer.stop()
            return

        scrambled = []
        for i, char in enumerate(self._full_text):
            if i < self._reveal_index:
                scrambled.append(char)
            elif char.isspace() or char in "#*-`_>[]()":
                scrambled.append(char)
            else:
                scrambled.append(random.choice(self._matrix_chars))
                
        self.update("".join(scrambled))


import asyncio
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import TextArea, Button, RichLog, Select

class BabelExecutor(Vertical):

    DEFAULT_CSS = """
    #babel-executor {
        height: 6;
        width: 100%;
        margin-bottom: 0;
    }

    .stdin-box {
        width: 75%;
        height: 100%;
    }

    #controls-box {
        width: 25%;
        height: 100%;
        layout: vertical;
        padding-left: 2;
    }

    #lang-select {
        width: 20;
        margin-bottom: 0;
    }

    #btn-run {
        width: 18;
        height: 3;
        margin-left: 1;
        content-align: center middle;
    }

    #exec-output {
        height: 1fr;
        width: 100%;
        background: $boost;
        border: solid;
    }
    """

    def compose(self) -> ComposeResult:
        with Horizontal(id="babel-executor"):
            yield TextArea(placeholder="stdinput:", id="exec-stdin-input", classes="stdin-box")
            
            with Vertical(id="controls-box"):
                yield Select(
                    options=[
                        ("Python", "python"),
                        ("C++", "cpp"),
                        ("C", "c"),
                        ("Bash", "bash")
                    ],
                    id="lang-select",
                    value="python",
                    allow_blank=False
                )
                yield Button("Run ▷", id="btn-run", variant="success", flat=True)
                
        yield RichLog(id="exec-output", highlight=True, markup=True)

    def on_select_changed(self, event: Select.Changed) -> None:
        if event.select.id == "lang-select":
            try:
                editor = self.screen.query_one("#code-input", TextArea)
                editor.language = str(event.value)
            except Exception:
                pass

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-run":
            await self.run_code()

    async def run_code(self) -> None:
        log = self.query_one("#exec-output", RichLog)
        stdin_data = self.query_one("#exec-stdin-input", TextArea).text
        lang = self.query_one("#lang-select", Select).value
        
        try:
            code_text = self.screen.query_one("#code-input", TextArea).text
        except Exception:
            log.write("[bold red]Error: Code not found in the editor.[/bold red]")
            return

        log.clear()
        log.write(f"[dim]Initializing {lang} environment...[/dim]")

        extensions = {"python": ".py", "cpp": ".cpp", "c": ".c", "bash": ".sh"}
        script_filename = f"/tmp/babel_temp_run{extensions.get(lang, '.txt')}"
        bin_filename = "/tmp/babel_temp_run_bin"
        
        with open(script_filename, "w") as f:
            f.write(code_text)

        if lang in ["c", "cpp"]:
            compiler = "c++" if lang == "cpp" else "cc"
            flags = ["-Wall"] if lang == "cpp" else ["-Wall"]
            
            log.write(f"[dim]Compiling with {compiler}...[/dim]")
            compile_proc = await asyncio.create_subprocess_exec(
                compiler, script_filename, "-o", bin_filename, *flags,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            c_out, c_err = await compile_proc.communicate()
            
            if compile_proc.returncode != 0:
                log.write(f"[bold red]Compilation error:[/bold red]\n{c_err.decode('utf-8', errors='ignore')}")
                return
            
            run_cmd = [bin_filename]
            
        elif lang == "python":
            run_cmd = ["python3", script_filename]
        elif lang == "bash":
            run_cmd = ["bash", script_filename]

        try:
            log.write("[dim]Executing program...[/dim]")
            process = await asyncio.create_subprocess_exec(
                *run_cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            input_bytes = stdin_data.encode("utf-8") if stdin_data else None
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(input=input_bytes), 
                timeout=5.0
            )

            if stdout:
                log.write(stdout.decode("utf-8", errors="ignore"))
            if stderr:
                log.write(f"[bold red]{stderr.decode('utf-8', errors='ignore')}[/bold red]")
                GlitchEffect(self.query_one("#exec-output"), 0.5)
                
            if not stdout and not stderr:
                log.write("[dim]Program executed with no output (empty stdout).[/dim]")

        except asyncio.TimeoutError:
            log.write("[bold red]Error: Timeout (infinite loop? > 5s).[/bold red]")
        except Exception as e:
            log.write(f"[bold red]Execution error: {e}[/bold red]")
            
        # log.write("[dim]--- End ---[/dim]")


from textual.widgets import TextArea

C_HIGHLIGHT_QUERY = """
(identifier) @variable

((identifier) @constant
 (#match? @constant "^[A-Z][A-Z\\d_]*$"))

"break" @keyword
"case" @keyword
"const" @keyword
"continue" @keyword
"default" @keyword
"do" @keyword
"else" @keyword
"enum" @keyword
"extern" @keyword
"for" @keyword
"if" @keyword
"inline" @keyword
"return" @keyword
"sizeof" @keyword
"static" @keyword
"struct" @keyword
"switch" @keyword
"typedef" @keyword
"union" @keyword
"volatile" @keyword
"while" @keyword

"#define" @keyword
"#elif" @keyword
"#else" @keyword
"#endif" @keyword
"#if" @keyword
"#ifdef" @keyword
"#ifndef" @keyword
"#include" @keyword
(preproc_directive) @keyword

"--" @operator
"-" @operator
"-=" @operator
"->" @operator
"=" @operator
"!=" @operator
"*" @operator
"&" @operator
"&&" @operator
"+" @operator
"++" @operator
"+=" @operator
"<" @operator
"==" @operator
">" @operator
"||" @operator

"." @delimiter
";" @delimiter

(string_literal) @string
(system_lib_string) @string

(null) @constant
(number_literal) @number
(char_literal) @number

(field_identifier) @property
(statement_identifier) @label
(type_identifier) @type
(primitive_type) @type
(sized_type_specifier) @type

(call_expression
  function: (identifier) @function)
(call_expression
  function: (field_expression
    field: (field_identifier) @function))
(function_declarator
  declarator: (identifier) @function)
(preproc_function_def
  name: (identifier) @function.special)

(comment) @comment
"""

CPP_QUERY = '(comment) @comment (string_literal) @string (number_literal) @number (true) @boolean (false) @boolean (this) @variable.builtin (identifier) @variable (type_identifier) @type (primitive_type) @type (field_identifier) @property (namespace_identifier) @namespace (statement_identifier) @label "class" @keyword "struct" @keyword "enum" @keyword "union" @keyword "template" @keyword "typename" @keyword "public" @keyword "private" @keyword "protected" @keyword "virtual" @keyword "new" @keyword "delete" @keyword "return" @keyword "if" @keyword "else" @keyword "while" @keyword "for" @keyword "do" @keyword "switch" @keyword "case" @keyword "break" @keyword "continue" @keyword "namespace" @keyword "using" @keyword "try" @keyword "catch" @keyword "throw" @keyword "friend" @keyword "operator" @keyword "const" @keyword "static" @keyword "constexpr" @keyword "inline" @keyword "typedef" @keyword "sizeof" @keyword "noexcept" @keyword "decltype" @keyword "final" @keyword "override" @keyword "explicit" @keyword "nullptr" @keyword "#define" @keyword "#include" @keyword "#if" @keyword "#endif" @keyword "#ifdef" @keyword "#ifndef" @keyword "#else" @keyword "#elif" @keyword (preproc_directive) @keyword "--" @keyword "++" @keyword "-" @keyword "+" @keyword "*" @keyword "/" @keyword "%" @keyword "=" @keyword "==" @keyword "!=" @keyword "<" @keyword ">" @keyword "<=" @keyword ">=" @keyword "&&" @keyword "||" @keyword "::" @keyword "." @keyword "->" @keyword ";" @keyword (call_expression function: (identifier) @function) (call_expression function: (field_expression field: (field_identifier) @function)) (function_declarator declarator: (identifier) @function)'



class BabelTextArea(TextArea):
    
    def on_mount(self) -> None:
        self._register_custom_languages()

    def _register_custom_languages(self) -> None:
        with open("/tmp/babel_debug.txt", "w") as debug_file:
            try:
                from tree_sitter import Language
                debug_file.write("[OK] tree_sitter imported.\n")
                
                from tree_sitter_c import language as c_lang
                self.register_language("c", Language(c_lang()), C_HIGHLIGHT_QUERY)
                debug_file.write("[OK] C language registered.\n")
                    
                from tree_sitter_cpp import language as cpp_lang
                self.register_language("cpp", Language(cpp_lang()), CPP_QUERY)
                debug_file.write("[OK] C++ language registered.\n")
                    
            except Exception as e:
                debug_file.write(f"[FATAL] Global tree_sitter error: {e}\n")

    def action_undo(self) -> None:
        self.cursor_location = (0, 0)
        try:
            super().action_undo()
        except Exception:
            pass


import asyncio
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Button, LoadingIndicator, RichLog, TextArea

class BabelPushTab(Vertical):

    DEFAULT_CSS = """

    #btn-push {
        width: 30;
        height: 3;
        margin-bottom: 2;
    }

    #push-loading {
        height: 3;
        display: none;
    }

    #push-output {
        width: 100%;
        height: 15;
        background: $boost;
        border: solid $panel;
        margin-top: 2;
    }
    """

    def compose(self) -> ComposeResult:
        yield Button("Push Actual Code", id="btn-push", variant="primary")
        yield LoadingIndicator(id="push-loading")
        yield RichLog(id="push-output", highlight=True, markup=True)

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-push":
            await self.handle_push()

    async def handle_push(self) -> None:
        btn = self.query_one("#btn-push", Button)
        loader = self.query_one("#push-loading", LoadingIndicator)
        log = self.query_one("#push-output", RichLog)

        code_text = ""
        try:
            editor = self.screen.query_one("#code-input", TextArea)
            code_text = editor.text
        except Exception:
            try:
                editor = self.app.query(TextArea).first()
                code_text = editor.text
            except Exception:
                log.write("[bold red]Error: No text editor found in the application.[/bold red]")
                return

        if not code_text.strip():
            log.write("[bold yellow]Warning: The editor is empty.[/bold yellow]")
            return

        btn.disabled = True
        loader.styles.display = "block"
        log.clear()
        log.write("[dim]Pushing code to Babel server...[/dim]")

        try:
            await asyncio.sleep(6.0) 
            # NOTE : push the code the server
            self.app.api_client.submit_code(1, editor.language, code_text)


            pass_test = False

            if pass_test:
                log.write("[bold green][✔] Code successfully pushed and queued![/bold green]")
                # btn.label = "you passed this challange"
                btn.disabled = True

            else:
                log.write("[bold red][X] Code faild to pass server tests![/bold red]")
                log.write("[bold red]Traces are available to find error![/bold red]")
                GlitchEffect(self.screen.query_one("#push-tab"), 0.7)
                btn.disabled = False


        except Exception as e:
            log.write(f"[bold red]Server communication error: {e}[/bold red]")

        finally:
            loader.styles.display = "none"
            # btn.disabled = False
