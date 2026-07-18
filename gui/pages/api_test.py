import io
import contextlib
from assets.theme import sizes, colors

from nicegui import ui

from utils.api_test import run_api_test

def build_api_test_page():

    with ui.card().classes('w-full'):

        ui.label('API Test').classes('text-h6')

        result = ui.log().classes('w-full h-96')

        def execute():

            buffer = io.StringIO()

            with contextlib.redirect_stdout(buffer):
                run_api_test()

            result.clear()

            for line in buffer.getvalue().splitlines():
                result.push(line)

        ui.button(
            text = 'Run Protocol Check', 
            on_click = execute,
            color = colors.GENERAL_BUTTON
        )