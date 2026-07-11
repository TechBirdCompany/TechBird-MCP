from nicegui import ui


def build_dmm_plot_tab():

    ui.label(
        "DMM Plot"
    )

    ui.input(
        "Filename"
    )

    ui.input(
        "Title"
    )

    ui.input(
        "Y Label"
    )

    ui.number(
        "Samples",
        value=200
    )

    ui.number(
        "Nominal"
    )

    ui.number(
        "Min"
    )

    ui.number(
        "Max"
    )

    ui.button(
        "Create Plot"
    )