from core import ft, asyncio
from views.layouts.main_layout import MainLayout
from controllers.update_controller import UpdateController

from core.logger import get_logger
logger = get_logger("App")

class UpdateView:
    def __init__(self, page, router):
        self.page = page
        self.router = router
        self.controller = UpdateController()
        self.progress = ft.ProgressBar(width=400, value=0, visible=False)
        self.status_text = ft.Text("", size=13, visible=False)
        self.btn_update = ft.TextButton(
            "Verificar atualização", on_click=self._on_check_click
        )
    
    def _refresh(self):
        """Chama page.update() de forma segura de qualquer thread."""
        try:
            self.page.update()
        except Exception:
            pass

    def _set_status(self, text: str, visible: bool = True):
        self.status_text.value = text
        self.status_text.visible = visible
        self._refresh()

    def render(self):
        self.status_text.visible = False
        self.progress.visible = False
        self.btn_update.disabled = False

        content = ft.Column(
            controls=[
                ft.Text(self.controller.get_title(), size=24),
                ft.Divider(),
                self.btn_update,
                self.status_text,
                self.progress,
            ],
            spacing=16,
        )

        layout = MainLayout(
            page=self.page,
            content=content,
            router=self.router,
        )

        self.page.run_task(self._check_update_async)
        return layout

    def _on_check_click(self, e):
        self.page.run_task(self._check_update_async)

    async def _check_update_async(self):
        self.btn_update.disabled = True
        self.status_text.value = "Verificando versão..."
        self.status_text.visible = True
        self._refresh()
        
        loop = asyncio.get_event_loop()
        remote = await loop.run_in_executor(None, self.controller.get_remote_version)

        if not remote:
            self.status_text.value = "Sem conexão ou falha ao verificar."
            self.btn_update.disabled = False
            self._refresh()
            return

        if not self.controller.needs_update(remote):
            self.status_text.value = "✓ Você já está na versão mais recente."
            self.btn_update.disabled = False
            self._refresh()
            return

        await self._show_dialog_async(remote)

    # ------------------------------------------------------------------
    # Dialog async
    # ------------------------------------------------------------------
    async def _show_dialog_async(self, remote: dict):
        confirmed = asyncio.Event()
        dismissed = asyncio.Event()

        def on_confirm(e):
            dlg.open = False
            self._refresh()
            confirmed.set()

        def on_dismiss(e):
            dlg.open = False
            self.btn_update.disabled = False
            self.status_text.value = "Atualização adiada."
            self._refresh()
            dismissed.set()

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Nova versão disponível"),
            content=ft.Text(
                f"Versão {remote['version']} disponível. Deseja atualizar agora?"
            ),
            actions=[
                ft.TextButton("Atualizar agora", on_click=on_confirm),
                ft.TextButton("Depois", on_click=on_dismiss),
            ],
        )

        self.page.overlay.append(dlg)
        dlg.open = True
        self._refresh()

        # Aguarda resposta do usuário sem bloquear a event loop
        while not confirmed.is_set() and not dismissed.is_set():
            await asyncio.sleep(0.1)

        if confirmed.is_set():
            await self._download_async(remote["url"])

    # ------------------------------------------------------------------
    # Download async com progresso
    # ------------------------------------------------------------------
    async def _download_async(self, url: str):
        self.progress.value = 0
        self.progress.visible = True
        self.status_text.visible = True
        self.status_text.value = "Iniciando download..."
        self._refresh()

        loop = asyncio.get_event_loop()
        last_pct_shown = [-1]

        def on_progress(pct):
            pct_int = int(pct * 100)
            if pct_int != last_pct_shown[0]:
                last_pct_shown[0] = pct_int
                self.progress.value = pct
                self.status_text.value = f"Baixando... {pct_int}%"
                # Agenda o refresh na event loop do Flet de forma thread-safe
                asyncio.run_coroutine_threadsafe(
                    self._async_refresh(), loop
                )

        try:
            exe = await loop.run_in_executor(
                None,
                lambda: self.controller.download_and_install(url, on_progress=on_progress),
            )
            self.status_text.value = "Download concluído. Iniciando instalação..."
            self.progress.value = 1.0
            self._refresh()
            await asyncio.sleep(0.5)
            self.controller.launch_installer_and_exit(exe)

        except Exception as ex:
            self.status_text.value = f"Erro no download: {ex}"
            logger.error(f"Erro no download: {ex}")
            self.btn_update.disabled = False
            self._refresh()

    async def _async_refresh(self):
        """Corrotina auxiliar para agendar page.update() na event loop."""
        try:
            self.page.update()
        except Exception:
            pass