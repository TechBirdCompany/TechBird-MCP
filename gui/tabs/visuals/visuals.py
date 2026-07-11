from nicegui import ui

from gui.tabs.visuals.scope_screenshot import (
    build_scope_screenshot_tab
)

from gui.tabs.visuals.dmm_screenshot import (
    build_dmm_screenshot_tab
)

from gui.tabs.visuals.dmm_plot import (
    build_dmm_plot_tab
)


def build_visuals_tab():

    with ui.tabs() as tabs:

        scope = ui.tab(
            "Scope Screenshot"
        )

        dmm_screen = ui.tab(
            "DMM Screenshot"
        )

        dmm_plot = ui.tab(
            "DMM Plot"
        )

    with ui.tab_panels(
        tabs,
        value=scope
    ).classes(
        "w-full"
    ):

        with ui.tab_panel(scope):
            build_scope_screenshot_tab()

        with ui.tab_panel(dmm_screen):
            build_dmm_screenshot_tab()

        with ui.tab_panel(dmm_plot):
            build_dmm_plot_tab()