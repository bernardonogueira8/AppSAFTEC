import asyncio
from core import ft, os
from views.layouts.main_layout import MainLayout
from controllers.plan_ceaf_controller import PlanCeafController


class Plan_ceafView:
    def __init__(self, page, router):
        self.page = page
        self.router = router
        self.controller = PlanCeafController()
        
        # Conecta os callbacks do controller às nossas funções thread-safe
        self.controller.on_progress = self._on_progress
        self.controller.on_status   = self._on_status
        self.controller.on_done     = self._on_done
        self.controller.on_error    = self._on_error

        # Variáveis de controle para o loop e otimização de progresso
        self._loop = None
        self._last_pct_shown = [-1]

        # Elementos de Interface
        self._path_field = ft.TextField(
            label="Arquivo selecionado",
            hint_text="Clique no ícone para selecionar um .xlsx",
            read_only=True,
            expand=True,
        )
        self._progress    = ft.ProgressBar(value=0, visible=False)
        self._status_text = ft.Text(
            "Aguardando seleção", size=13,
            color=ft.Colors.SECONDARY,
        )
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
        self._output_dir = ""
        self.file_picker = ft.FilePicker()

    async def _async_refresh(self):
        """Corrotina auxiliar para agendar page.update() na event loop principal do Flet."""
        try:
            self.page.update()
        except Exception:
            pass

    def _refresh(self):
        """Atualização síncrona segura baseada no estado do loop."""
        if self._loop:
            asyncio.run_coroutine_threadsafe(self._async_refresh(), self._loop)
        else:
            self.page.update()

    async def pick_file_handler(self, e):
        try:
            result = await self.file_picker.pick_files(
                allow_multiple=False,
                allowed_extensions=["xlsx", "xls"]
            )
            
            if result:
                path = result[0].path
                self._path_field.value = path
                self.controller.set_file_path(path)
                
                self._btn_process.disabled = False
                self._btn_open.visible = False
                self._progress.value = 0
                self._progress.visible = False
                self._status_text.value = "Pronto para processar."
                self._status_text.color = ft.Colors.SECONDARY
                self.page.update()
        except Exception as ex:
            print(f"Erro ao selecionar arquivo: {ex}")

    def render(self):
        if self.file_picker not in self.page.services:
            self.page.services.append(self.file_picker)
            self.page.update()

        content = ft.Column(
            spacing=20,
            controls=[
                ft.Text(self.controller.get_title(), size=24,
                        weight=ft.FontWeight.W_500),
                ft.Divider(),
                ft.Row(controls=[
                    self._path_field,
                    ft.IconButton(
                        icon=ft.Icons.UPLOAD_FILE,
                        tooltip="Selecionar arquivo",
                        on_click=self.pick_file_handler,
                    ),
                ]),
                ft.Row(controls=[self._btn_process, self._btn_open], spacing=12),
                self._status_text,
                self._progress,
            ],
        )
        return MainLayout(page=self.page, content=content, router=self.router)

    async def _on_start(self, e):
        # Captura a event loop ativa da UI do Flet
        self._loop = asyncio.get_event_loop()
        self._last_pct_shown[0] = -1

        # Prepara a UI para o início do processo
        self._btn_process.disabled = True
        self._btn_open.visible = False
        self._progress.value = 0
        self._progress.visible = True
        self._status_text.value = "Iniciando processamento dos dados..."
        self._refresh()

        try:
            # Executa a regra de negócio pesada do controller em um Executor (Thread separada)
            # impedindo que a janela do app congele
            await self._loop.run_in_executor(
                None,
                lambda: self.controller.start_processing()
            )
        except Exception as ex:
            self._on_error(str(ex))

    # --- Callbacks acionados pela Thread do Controller ---

    def _on_progress(self, pct: float):
        pct_int = int(pct * 100)
        # Evita enfileirar atualizações redundantes de UI se o percentual inteiro não mudou
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
        self._refresh()

    def _on_error(self, msg: str):
        self._status_text.value = f"Erro: {msg}"
        self._status_text.color = ft.Colors.ERROR
        self._btn_process.disabled = False
        self._progress.visible = False
        self._refresh()