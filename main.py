from configs.app_config import AppConfig
from core.logger import get_logger
from core.error_handler import GlobalErrorHandler
from core import ft, threading
import runtime_imports
from configs.routes import ROUTES

logger = get_logger("App")

def _check_update_background(page: ft.Page, router):
    try:
        from controllers.update_controller import UpdateController
        remote = UpdateController.get_remote_version()
        if not remote or not UpdateController.needs_update(remote):
            return

        def on_confirm(e):
            dlg.open = False
            page.update()
            router.navigate("/update")
            
        def on_dismiss(e):
            dlg.open = False
            page.update()

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Nova versão disponível"),
            content=ft.Text(
                f"Versão {remote['version']} disponível.\nDeseja atualizar agora?"
            ),
            actions=[
                ft.TextButton("Atualizar agora", on_click=on_confirm),
                ft.TextButton("Depois", on_click=on_dismiss),
            ],
        )
        page.overlay.append(dlg)
        dlg.open = True
        page.update()

    except Exception as e:
        logger.warning(f"Falha na verificação de update: {e}")

def main(page: ft.Page):
    try:
        page.assets_dir = "assets"

        if page.platform in (
            ft.PagePlatform.WINDOWS,
            ft.PagePlatform.LINUX,
            ft.PagePlatform.MACOS,
        ):
            from core.app import FletingApp

            page.window.width = AppConfig.DEFAULT_SCREEN["width"]
            page.window.height = AppConfig.DEFAULT_SCREEN["height"]

        from core.i18n import I18n

        I18n.load("pt")

        from core.router import Router
        from configs.routes import routes

        router = Router(page)
        router.navigate("/")

        # Verifica update em background sem travar a UI
        threading.Thread(
            target=_check_update_background,
            args=(page, router),
            daemon=True
        ).start()
        
        logger.info("Aplicação iniciada com sucesso")

    except Exception as e:
        GlobalErrorHandler.handle(page, e)


ft.app(main)
