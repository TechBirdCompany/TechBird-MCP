from nicegui import ui

console = None


def build_console():

    global console

    ui.separator()

    ui.label('Console').classes('text-h6')

    console = ui.log().classes('w-full h-48')

    return console