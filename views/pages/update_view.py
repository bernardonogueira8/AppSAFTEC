from core import ft, threading
from views.layouts.main_layout import MainLayout
from controllers.update_controller import UpdateController

class UpdateView:
    def __init__(self, page, router):
        self.page = page
        self.router = router
        self.controller = UpdateController()

    def render(self):
        progress = ft.ProgressBar(width=400, value=0, visible=False)
        status_text = ft.Text("", size=13, visible=False)
        btn_update = ft.ElevatedButton("Verificar atualização", on_click=self._check_update)

        self._progress = progress
        self._status = status_text
        self._btn = btn_update

        content = ft.Column(
            controls=[
                ft.Text(self.controller.get_title(), size=24),
                ft.Divider(),
                btn_update,
                status_text,
                progress,
            ],
            spacing=16,
        )
        return MainLayout(
            page=self.page,
            content=content,
            router=self.router,
        )

    def _check_update(self, e=None):
        self._btn.disabled = True
        self._status.value = "Verificando versão..."
        self._status.visible = True
        self.page.update()
        threading.Thread(target=self._run_check, daemon=True).start()

    def _run_check(self):
        remote = UpdateController.get_remote_version()

        if not remote:
            self._status.value = "Sem conexão ou falha ao verificar."
            self._btn.disabled = False
            self.page.update()
            return

        if not UpdateController.needs_update(remote):
            self._status.value = "✓ Você já está na versão mais recente."
            self._btn.disabled = False
            self.page.update()
            return

        self._show_update_dialog(remote)

    def _show_update_dialog(self, remote: dict):
        def on_confirm(e):
            dlg.open = False
            self.page.update()
            self._start_download(remote["url"])

        def on_dismiss(e):
            dlg.open = False
            self._btn.disabled = False
            self._status.value = "Atualização adiada."
            self.page.update()

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Nova versão disponível"),
            content=ft.Text(f"Versão {remote['version']} disponível. Deseja atualizar agora?"),
            actions=[
                ft.TextButton("Atualizar agora", on_click=on_confirm),
                ft.TextButton("Depois", on_click=on_dismiss),
            ],
        )
        self.page.overlay.append(dlg)
        dlg.open = True
        self.page.update()

    def _start_download(self, url: str):
        self._progress.value = 0
        self._progress.visible = True
        self._status.visible = True
        self._status.value = "Iniciando download..."
        self.page.update()

        def on_progress(pct):
            self._progress.value = pct
            self._status.value = f"Baixando... {int(pct * 100)}%"
            self.page.update()

        def do_download():
            try:
                exe = UpdateController.download_and_install(url, on_progress=on_progress)
                self._status.value = "Download concluído. Iniciando instalação..."
                self.page.update()
                UpdateController.launch_installer_and_exit(exe)
            except Exception as ex:
                self._status.value = f"Erro no download: {ex}"
                self._btn.disabled = False
                self.page.update()

        threading.Thread(target=do_download, daemon=True).start()