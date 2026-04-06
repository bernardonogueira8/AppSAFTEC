
import flet as ft
import importlib

ROUTES = [
    


    {
        "path": "/test",
        "view": "views.pages.test_view.TestView",
        "label": "Test",
        "icon": ft.Icons.CHEVRON_RIGHT,
        "show_in_top": True,
        "show_in_bottom": False,
    },

    {
        "path": "/",
        "view": "views.pages.home_view.HomeView",
        "label": "menu.home",
        "icon": ft.Icons.HOME,
        "show_in_top": True,
        "show_in_bottom": True,
    },
    {
        "path": "/help",
        "view": "views.pages.help_view.HelpView",
        "label": "menu.help",
        "icon": ft.Icons.HELP,
        "show_in_top": True,
        "show_in_bottom": True,
    },
    {
        "path": "/exit",
        "view": "views.pages.exit_view.ExitView",
        "label": "Exit",
        "icon": ft.Icons.CHEVRON_RIGHT,
        "show_in_top": False,
        "show_in_bottom": True,
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

