import os
from nicegui import ui, app
from gui.pages.scope_screenshot import build_scope_screenshot_page
from gui.pages.api_test import build_api_test_page
from gui.pages.load_test import build_load_test_page
from gui.pages.get_plot import build_get_plot_page
from gui.pages.configuration import build_configuration_page

def build_main_page():

    # ---------------------------
    # UI row with name and logo
    # ---------------------------

    with ui.row().classes('w-full justify-between items-center'):

        ui.label('TechBird - Master Control Programm').classes('text-h4')

        logo = ui.image('assets/TechBird_Logo.png').style(
            '''
            width:100px;
            height:100px;
            '''
        )

        logo.tooltip('Double click to exit')

        logo.on('dblclick',lambda: os._exit(0))

    # ---------------------------
    # UI row with menus
    # ---------------------------

    with ui.row().classes('w-full'):

        # ---------------------------
        # Side menu
        # ---------------------------

        with ui.card().style('width:250px; min-height:600px;'):

            ui.label('Navigation').classes('text-h6')

            nav_scope = ui.button('Scope Screenshot').classes('w-full')

            nav_plot = ui.button('DMM Plot').classes('w-full')

            nav_load = ui.button('Load Test').classes('w-full')

            nav_api = ui.button('API Test').classes('w-full')
    
            nav_config = ui.button('Configuration').classes('w-full')

        content = ui.column().classes('flex-grow')

        # ---------------------------
        # Menu definitions
        # ---------------------------   

        def show_scope():

            content.clear()

            with content:
                build_scope_screenshot_page()

        def show_load():

            content.clear()

            with content:
                build_load_test_page()

        def show_plot():

            content.clear()

            with content:
                build_get_plot_page()

        def show_api():

            content.clear()

            with content:
                build_api_test_page()

        def show_config():

            content.clear()

            with content:
                build_configuration_page()

        # ---------------------------
        # Button Functions
        # ---------------------------

        nav_scope.on('click', show_scope)

        nav_load.on('click', show_load)

        nav_plot.on('click', show_plot)

        nav_api.on('click', show_api)

        nav_config.on('click', show_config)

        # ---------------------------
        # Default  Page
        # ---------------------------

        with content:
            build_scope_screenshot_page()