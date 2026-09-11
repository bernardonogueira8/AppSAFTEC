from core import ft, os, asyncio
from views.layouts.main_layout import MainLayout
from controllers.emailceaf_controller import EmailceafController

class EmailceafView:
    def __init__(self, page, router):
        self.page = page
        self.router = router
        self.controller = EmailceafController(page=self.page)
        self.system_name = "E-mail"
        self.templates = {} 

        self.controller.on_progress = self._on_progress
        self.controller.on_status   = self._on_status
        self.controller.on_done     = self._on_done
        self.controller.on_error    = self._on_error

        self._loop = None
        self._last_pct_shown = [-1]

        # Elementos de Interface (Feedback)
        self._progress    = ft.ProgressBar(value=0, visible=False)
        self._status_text = ft.Text("Aguardando seleção", size=13, color=ft.Colors.SECONDARY)
        
        self._btn_process = ft.Button(
            "Iniciar processamento",
            icon=ft.Icons.PLAY_ARROW_ROUNDED,
            on_click=self._on_start,
            disabled=True,
        )
        
        self._btn_open = ft.TextButton(
            "Abrir pasta de saída",
            icon=ft.Icons.FOLDER_OPEN,
            visible=False,
            on_click=lambda e: os.startfile(self._output_dir),
        )
        self._btn_open = ft.TextButton(
                    "Abrir pasta de saída",
                    icon=ft.Icons.FOLDER_OPEN,
                    visible=False,
                    on_click=lambda e: os.startfile(self._output_dir),
                )
        self._btn_voltar = ft.Button(content=ft.Text("Voltar"),on_click=self.voltar_passo)
        
        self._output_dir = ""

        # --- 1. INSTANCIANDO OS FILE PICKERS (Sem on_result) ---
        self.picker_planilha = ft.FilePicker()
        self.picker_pasta1 = ft.FilePicker()
        self.picker_pasta2 = ft.FilePicker()
        # Não adicionamos na página aqui no __init__! Vamos fazer isso no render.

    # --- 2. CALLBACKS ASSÍNCRONOS (Igual ao Plan_ceafView) ---
    async def pick_planilha_handler(self, e):
        try:
            result = await self.picker_planilha.pick_files(
                allow_multiple=False,
                allowed_extensions=["xlsx", "xls"]
            )
            if result:
                path = result[0].path
                self._path_field.value = path
                self.controller.set_file_path(path)
                self._check_ready_to_process()
                self.page.update()
        except Exception as ex:
            print(f"Erro ao selecionar planilha: {ex}")

    async def pick_pasta1_handler(self, e):
        try:
            result = await self.picker_pasta1.get_directory_path()
            if result:
                self.pasta1_field.value = result
                self.controller.set_pasta1_path(result)
                self._check_ready_to_process()
                self.page.update()
        except Exception as ex:
            print(f"Erro ao selecionar pasta 1: {ex}")

    async def pick_pasta2_handler(self, e):
        try:
            result = await self.picker_pasta2.get_directory_path()
            if result:
                self.pasta2_field.value = result
                self.controller.set_pasta2_path(result)
                self._check_ready_to_process()
                self.page.update()
        except Exception as ex:
            print(f"Erro ao selecionar pasta 2: {ex}")

    # --- LÓGICA CONDICIONAL ---
    def _check_ready_to_process(self):
        has_planilha = bool(self._path_field.value)
        has_pasta1 = bool(self.pasta1_field.value)
        has_pasta2 = bool(self.pasta2_field.value)
        tipo = self.radio_tipo.value
        
        if tipo == "complementar":
            if has_planilha and has_pasta1:
                self._btn_process.disabled = False
        elif tipo == "regular":
            if has_planilha and has_pasta1 and has_pasta2:
                self._btn_process.disabled = False
        else:
            self._btn_process.disabled = True

    def on_program_change(self, e):
        tipo = self.radio_tipo.value
        if tipo == "complementar":
            self.row_pasta1.visible = True
            self.row_pasta2.visible = False
            self.pasta2_field.value = "" 
        elif tipo == "regular":
            self.row_pasta1.visible = True
            self.row_pasta2.visible = True
        
        self._check_ready_to_process()
        self.page.update()

    # --- REFRESHES ASÍNCRONOS ---
    async def _async_refresh(self):
        try:
            self.page.update()
        except Exception:
            pass

    def _refresh(self):
        if self._loop:
            asyncio.run_coroutine_threadsafe(self._async_refresh(), self._loop)
        else:
            self.page.update()

    def render(self):
        # ADICIONANDO OS PICKERS NA PÁGINA COM SEGURANÇA (Igual ao seu código base)
        pickers = [self.picker_planilha, self.picker_pasta1, self.picker_pasta2]
        
        # O seu exemplo original usava page.services, mas o padrão do Flet é page.overlay. 
        # Vou usar page.overlay. Se o seu framework exigir 'services', troque 'overlay' por 'services'.
        for p in pickers:
            if p not in self.page.services:
                self.page.services.append(p)
        self.page.update()

        credenciais_salvas = self.controller.load_saved_credentials(self.system_name)
        user_padrao = credenciais_salvas[0] if credenciais_salvas else ""
        pass_padrao = credenciais_salvas[1] if credenciais_salvas else ""

        # --- CAMPOS DA TELA DE LOGIN ---
        self.user_input = ft.TextField(
            label=f"E-mail:", value=user_padrao, prefix_icon=ft.Icons.PERSON_OUTLINE, 
            border_radius=10, expand=True, filled=True,
        )
        self.pass_input = ft.TextField(
            label=f"Senha do {self.system_name}:", password=True, can_reveal_password=True, 
            expand=True, value=pass_padrao, prefix_icon=ft.Icons.LOCK_OUTLINE, 
            border_radius=10, filled=True,
        )
        
        self.login_step = ft.Column(
            controls=[
                ft.Icon(ft.Icons.ACCOUNT_CIRCLE, size=70, color=ft.Colors.BLUE_700),
                ft.Text(f"Autenticação {self.system_name}", size=26, weight=ft.FontWeight.BOLD),
                ft.Text("Verifique suas credenciais para acessar a automação.", color=ft.Colors.GREY_500),
                self.user_input,
                self.pass_input,
                ft.Button(
                    content=ft.Row(
                        controls=[
                            ft.Text("Acessar e Continuar", color=ft.Colors.WHITE, size=16, weight=ft.FontWeight.W_600),
                            ft.Icon(ft.Icons.ARROW_FORWARD, color=ft.Colors.WHITE),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE_700, shape=ft.RoundedRectangleBorder(radius=10), padding=ft.Padding.all(20)),
                    on_click=self.avancar_passo,
                ),
            ],
            visible=True, 
            expand=True, 
            alignment=ft.MainAxisAlignment.CENTER, 
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

        # --- CAMPOS DA TELA DE AUTOMAÇÃO ---
        self.radio_tipo = ft.RadioGroup(
            content=ft.Row([
                ft.Radio(value="regular", label="Programação Regular"),
                ft.Radio(value="complementar", label="Programação Complementar")
            ]),
            on_change=self.on_program_change
        )

        self.pasta1_field = ft.TextField(label="Selecionar Pasta das Planilhas da Unidade", read_only=True, expand=True)
        self.row_pasta1 = ft.Row(
            controls=[
                self.pasta1_field,
                # APONTANDO PARA A NOVA FUNÇÃO ASSÍNCRONA
                ft.IconButton(icon=ft.Icons.FOLDER, on_click=self.pick_pasta1_handler)
            ],
            visible=False 
        )

        self.pasta2_field = ft.TextField(label="Selecionar Pasta das Planilhas do BI", read_only=True, expand=True)
        self.row_pasta2 = ft.Row(
            controls=[
                self.pasta2_field,
                # APONTANDO PARA A NOVA FUNÇÃO ASSÍNCRONA
                ft.IconButton(icon=ft.Icons.FOLDER, on_click=self.pick_pasta2_handler)
            ],
            visible=False 
        )

        self._path_field = ft.TextField(label="Planilha Controle", hint_text="Selecione um arquivo .xlsx", read_only=True, expand=True)
        self.row_planilha = ft.Row([
            self._path_field,
            # APONTANDO PARA A NOVA FUNÇÃO ASSÍNCRONA
            ft.IconButton(icon=ft.Icons.ATTACH_FILE, on_click=self.pick_planilha_handler)
        ])

        self.automation_step = ft.Column(
            controls=[
                ft.Text(self.controller.get_title(), size=24, weight=ft.FontWeight.W_500),
                ft.Divider(height=20, color="transparent"),
                
                ft.Text("1. Selecione o tipo de programação:", weight=ft.FontWeight.W_500),
                self.radio_tipo,
                
                ft.Divider(height=10, color="transparent"),
                self.row_pasta1,
                self.row_pasta2,
                
                ft.Divider(height=10, color="transparent"),
                ft.Text("2. Selecione a planilha de controle:", weight=ft.FontWeight.W_500),
                self.row_planilha,
                
                ft.Divider(height=20, color="transparent"),
                self._status_text,
                self._progress,
                ft.Row([self._btn_process, self._btn_open, self._btn_voltar]),
            ],
            visible=False,
            expand=True,
            alignment=ft.MainAxisAlignment.START,
        )


        content = ft.Column(
            controls=[self.login_step, self.automation_step],
            scroll=ft.ScrollMode.AUTO,
            spacing=20,
        )

        # Note: Envolto no MainLayout assim como no seu arquivo funcional
        return MainLayout(page=self.page, content=content, router=self.router)

    # --- FUNÇÕES DO BOTÃO INICIAR E CALLBACKS DA THREAD ---
    async def _on_start(self, e):
        self._loop = asyncio.get_event_loop()
        self._last_pct_shown[0] = -1

        self._btn_process.disabled = True
        self._btn_open.visible = False
        self._progress.value = 0
        self._progress.visible = True
        self._status_text.value = "Iniciando processamento dos dados..."
        self._refresh()

        try:
            await self._loop.run_in_executor(
                None,
                lambda: self.controller.start_processing()
            )
        except Exception as ex:
            self._on_error(str(ex))

    def _on_progress(self, pct: float):
        pct_int = int(pct * 100)
        if pct_int != self._last_pct_shown[0]:
            self._last_pct_shown[0] = pct_int
            self._progress.value = pct
            self._refresh()

    def _on_status(self, msg: str):
        self._status_text.value = msg
        self._refresh()

    def _on_done(self, output_dir: str):
        self._output_dir = output_dir
        self._status_text.value = "Concluído com sucesso!"
        self._status_text.color = ft.Colors.GREEN
        self._btn_process.disabled = False
        self._btn_open.visible = True
        self._progress.visible = False
        self._refresh()

    def _on_error(self, msg: str):
        self._status_text.value = f"Erro: {msg}"
        self._status_text.color = ft.Colors.ERROR
        self._btn_process.disabled = False
        self._progress.visible = False
        self._refresh()
        
    def voltar_passo(self, e):
        self.automation_step.visible = False
        self.login_step.visible = True
        self.page.update()
    
    def avancar_passo(self, e):
        sucesso = self.controller.save_credentials(
            self.user_input.value, self.pass_input.value, self.system_name
        )
        if sucesso:
            self.login_step.visible = False
            self.automation_step.visible = True
            self.page.update()
    