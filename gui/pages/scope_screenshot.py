from nicegui import ui
from loguru import logger

from gui.config import load_config, create_device
from tools.get_visual import get_screenshot_scope

def build_scope_screenshot_page():

    preview = None

    def create_screenshot():

        try:

            cfg = load_config()

            scope = create_device(
                cfg["selected"]["scope"]
            )

            image_path = get_screenshot_scope(
                device=scope,
                filename=filename.value,
                label_ch1=ch1.value,
                label_ch2=ch2.value,
                label_ch3=ch3.value,
                label_ch4=ch4.value,
            )

            preview.set_source(image_path)

            ui.notify("Screenshot created", type="positive")

        except Exception as e:

            logger.exception(e)

            ui.notify(str(e), type="negative")

    with ui.row().classes('w-full').style('align-items:flex-start'):

        with ui.card().style('width:350px;'):

            ui.label('Parameters').classes('text-h6')

            filename = ui.input('Filename',value='TEST').classes('w-full')

            ch1 = ui.input('CH1 Label').classes('w-full')

            ch2 = ui.input('CH2 Label').classes('w-full')

            ch3 = ui.input('CH3 Label').classes('w-full')

            ch4 = ui.input('CH4 Label').classes('w-full')

            ui.button('Create Screenshot', on_click=create_screenshot).classes('w-full')

        with ui.card().style(
            '''
            flex:1;
            display:flex;
            justify-content:center;
            align-items:center;
            '''
        ):

            preview = ui.image().style(
                '''
                width:1024;
                max-width:90%;
                border:1px solid #444;
                '''
            )






