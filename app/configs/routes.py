
import flet as ft
import importlib

ROUTES = [
    {
        "path": "/sei_dma",
        "view": "views.pages.sei_dma_view.Sei_dmaView",
        "label": "sei.Sei_dma",
        "icon": ft.Icons.CHEVRON_RIGHT,
        "show_in_top": False,
        "show_in_slidebar": True,
    },

    {
        "path": "/",
        "view": "views.pages.home_view.HomeView",
        "label": "menu.home",
        "icon": ft.Icons.HOME,
        "show_in_top": True,
        "show_in_slidebar": False,
    },
    {
        "path": "/help",
        "view": "views.pages.help_view.HelpView",
        "label": "menu.help",
        "icon": ft.Icons.HELP,
        "show_in_top": False,
        "show_in_slidebar": True,
    },
    {
        "path": "/exit",
        "view": "views.pages.exit_view.ExitView",
        "label": "menu.exit",
        "icon": ft.Icons.CLOSE,
        "show_in_top": True,
        "show_in_slidebar": False,
    },
    
]

def load_view(view_path: str):
    module_name, class_name = view_path.rsplit(".", 1)
    
    try:
        module = importlib.import_module(module_name)
        view_class = getattr(module, class_name)
        return view_class
    except (ImportError, AttributeError) as e:
        print(f"Erro ao carregar view {view_path}: {e}")
        return None

def get_routes():
    routes = {}

    for r in ROUTES:
        def create_view_lambda(path=r["view"]):
            return lambda page, router: load_view(path)(page, router).render()

        routes[r["path"]] = create_view_lambda()

    return routes

routes = get_routes()

