import flet as ft
import importlib

ROUTES = [
    {
        "path": "/plan_ceaf",
        "view": "views.pages.plan_ceaf_view.Plan_ceafView",
        "label": "outros.plan_ceaf",
        "icon": ft.Icons.CHEVRON_RIGHT,
        "show_in_top": True,
        "show_in_bottom": False,
    },
    {
        "path": "/simpas_estoque",
        "view": "views.pages.simpas_estoque_view.Simpas_estoqueView",
        "label": "simpas.estoque",
        "icon": ft.Icons.CHEVRON_RIGHT,
        "show_in_top": False,
        "show_in_bottom": False,
    },
    {
        "path": "/simpas_entradas_saidas",
        "view": "views.pages.simpas_entradas_saidas_view.Simpas_entradas_saidasView",
        "label": "simpas.entradas_saidas",
        "icon": ft.Icons.CHEVRON_RIGHT,
        "show_in_top": True,
        "show_in_bottom": False,
    },
    {
        "path": "/sigaf_contrapartida",
        "view": "views.pages.sigaf_contrapartida_view.Sigaf_contrapartidaView",
        "label": "sigaf.contrapartida",
        "icon": ft.Icons.CHEVRON_RIGHT,
        "show_in_top": True,
        "show_in_bottom": False,
    },
    {
        "path": "/sigaf_prefeitura",
        "view": "views.pages.sigaf_prefeitura_view.Sigaf_prefeituraView",
        "label": "sigaf.prefeitura",
        "icon": ft.Icons.CHEVRON_RIGHT,
        "show_in_top": True,
        "show_in_bottom": False,
    },
    {
        "path": "/esus_treina",
        "view": "views.pages.esus_treina_view.Esus_treinaView",
        "label": "outros.esus_treina",
        "icon": ft.Icons.CHEVRON_RIGHT,
        "show_in_top": True,
        "show_in_bottom": False,
    },
    {
        "path": "/sei_caj",
        "view": "views.pages.sei_caj_view.Sei_cajView",
        "label": "sei.caj",
        "icon": ft.Icons.CHEVRON_RIGHT,
        "show_in_top": True,
        "show_in_bottom": False,
    },
    {
        "path": "/sei_dma",
        "view": "views.pages.sei_dma_view.Sei_dmaView",
        "label": "sei.dma",
        "icon": ft.Icons.CHEVRON_RIGHT,
        "show_in_top": True,
        "show_in_bottom": False,
    },
    {
        "path": "/",
        "view": "views.pages.home_view.HomeView",
        "label": "menu.home",
        "icon": ft.Icons.HOME,
        "show_in_top": False,
        "show_in_bottom": True,
    },
    {
        "path": "/help",
        "view": "views.pages.help_view.HelpView",
        "label": "menu.help",
        "icon": ft.Icons.HELP,
        "show_in_top": True,
        "show_in_bottom": False,
    },
    {
        "path": "/exit",
        "view": "views.pages.exit_view.ExitView",
        "label": "menu.exit",
        "icon": ft.Icons.CLOSE,
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
