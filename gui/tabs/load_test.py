from nicegui import ui


def build_load_test_tab():

    ui.input(
        "Domain"
    )

    ui.number(
        "Voltage"
    )

    ui.number(
        "Min Voltage"
    )

    ui.number(
        "Max Voltage"
    )

    ui.number(
        "Current"
    )

    ui.number(
        "Samples",
        value=200
    )

    ui.checkbox(
        "Single Measurement"
    )

    ui.button(
        "Start Load Test"
    )