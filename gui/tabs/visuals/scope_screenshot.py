from nicegui import ui


def build_scope_screenshot_tab():

    ui.label(
        "Scope Screenshot"
    )

    filename = ui.input(
        "Filename"
    )

    ch1 = ui.input(
        "CH1 Label"
    )

    ch2 = ui.input(
        "CH2 Label"
    )

    ch3 = ui.input(
        "CH3 Label"
    )

    ch4 = ui.input(
        "CH4 Label"
    )

    ui.button(
        "Create Screenshot"
    )