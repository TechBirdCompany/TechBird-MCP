from nicegui import ui
from loguru import logger
import threading

from gui.config import (
    load_config,
    create_device,
)

from tools.test_load import test_load


def build_load_test_page():

    test_results = []
    last_result_count = 0

    gallery = None
    dialog = None
    preview = None

    def open_preview(image_path):

        preview.set_source(image_path)
        preview.update()

        dialog.open()

    def show_results(files):

        gallery.clear()

        with gallery:

            for file in files[:9]:

                image_path = file.replace(
                    "\\",
                    "/"
                )

                image = ui.image(
                    image_path
                ).style(
                    '''
                    width:350px;
                    height:auto;
                    cursor:pointer;
                    margin:auto;
                    '''
                )

                image.tooltip(
                    image_path.split("/")[-1]
                )

                image.on(
                    'click',
                    lambda e, p=image_path:
                        open_preview(p)
                )

    def check_for_results():

        nonlocal test_results
        nonlocal last_result_count

        if not test_results:
            return

        if len(test_results) == last_result_count:
            return

        last_result_count = len(test_results)

        show_results(
            test_results
        )

    def run_load_test():

        nonlocal test_results

        try:

            cfg = load_config()

            scope = create_device(
                cfg["selected"]["scope"]
            )

            dmm = create_device(
                cfg["selected"]["dmm"]
            )

            eload = create_device(
                cfg["selected"]["eload"]
            )

            test_results = test_load(
                scope=scope,
                dmm=dmm,
                eload=eload,
                voltage=float(voltage.value),
                max_voltage=float(
                    max_voltage.value
                ),
                min_voltage=float(
                    min_voltage.value
                ),
                domain=domain.value,
                current=float(
                    current.value
                ),
                samples=int(
                    samples.value
                ),
                single=single.value,
            )

            logger.info(
                'Load Test completed'
            )

        except Exception as e:

            logger.exception(e)

    with ui.row().classes(
        'w-full'
    ).style(
        'align-items:flex-start'
    ):

        #
        # Parameters
        #
        with ui.card().style(
            'width:500px;'
        ):

            ui.label(
                'Load Test'
            ).classes(
                'text-h6'
            )

            domain = ui.input(
                'Domain',
                value='VCC_5V0'
            ).classes(
                'w-full'
            )

            voltage = ui.number(
                'Voltage',
                value=5.0
            ).classes(
                'w-full'
            )

            min_voltage = ui.number(
                'Min Voltage',
                value=4.95
            ).classes(
                'w-full'
            )

            max_voltage = ui.number(
                'Max Voltage',
                value=5.05
            ).classes(
                'w-full'
            )

            current = ui.number(
                'Current',
                value=0.5
            ).classes(
                'w-full'
            )

            samples = ui.number(
                'Samples',
                value=200
            ).classes(
                'w-full'
            )

            single = ui.checkbox(
                'Single Measurement'
            )

            ui.button(
                'Start Load Test',
                on_click=lambda: threading.Thread(
                    target=run_load_test,
                    daemon=True
                ).start()
            ).classes(
                'w-full'
            )

        #
        # Results
        #
        with ui.card().style(
            'flex:1;'
        ):

            ui.label(
                'Generated Files'
            ).classes(
                'text-h6'
            )

            dialog = ui.dialog().props(
                'maximized'
            )

            with dialog:

                preview = ui.image().style(
                    '''
                    max-width:95vw;
                    max-height:95vh;
                    object-fit:contain;
                    '''
                )

            gallery = ui.grid(
                columns=3
            ).classes(
                'w-full'
            ).style(
                'justify-items:center;'
            )

    ui.timer(
        1.0,
        check_for_results
    )