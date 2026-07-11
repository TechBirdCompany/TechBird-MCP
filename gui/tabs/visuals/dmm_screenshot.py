from nicegui import ui


def build_dmm_screenshot_tab():

    ui.label(
        "DMM Screenshot"
    ).classes(
        "text-h6"
    )

    ui.input(
        label="Filename"
    )

    ui.button(
        "Create Screenshot"
    )