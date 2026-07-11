from nicegui import ui

from gui.tabs.api_test import build_api_test_tab
from gui.tabs.load_test import build_load_test_tab
from gui.tabs.visuals.visuals import build_visuals_tab


def build_main_page():

    ui.label(
        "TechBird MCP"
    ).classes(
        "text-h4"
    )

    with ui.card().classes("w-full"):

        ui.label(
            "Connected Devices"
        )

        with ui.row():

            ui.input(
                "Scope",
                value="Siglent SDS2000"
            )

            ui.button(
                "Connect"
            )

        with ui.row():

            ui.input(
                "DMM",
                value="OWON XDM1000"
            )

            ui.button(
                "Connect"
            )

        with ui.row():

            ui.input(
                "E-Load",
                value="EASTTESTER ET54"
            )

            ui.button(
                "Connect"
            )

    with ui.tabs().classes(
        "w-full"
    ) as tabs:

        api_tab = ui.tab("API Test")
        visual_tab = ui.tab("Visuals")
        load_tab = ui.tab("Load Test")

    with ui.tab_panels(
        tabs,
        value=api_tab
    ).classes(
        "w-full"
    ):

        with ui.tab_panel(api_tab):
            build_api_test_tab()

        with ui.tab_panel(visual_tab):
            build_visuals_tab()

        with ui.tab_panel(load_tab):
            build_load_test_tab()

    ui.separator()

    ui.label(
        "Console"
    ).classes(
        "text-h6"
    )

    ui.log().classes(
        "w-full h-64"
    )