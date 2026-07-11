from nicegui import ui
from loguru import logger

from devices.dmm.owon_xdm1000.owon_xdm_1000 import (
    OWON_XDM1000
)

from tools.get_visual import (
    get_plot_dmm
)


def build_get_plot_page():

    preview = None

    def create_plot():

        try:

            dmm = OWON_XDM1000()

            image_path = get_plot_dmm(
                device=dmm,
                filename=filename.value,
                samples=int(samples.value),
                title=title.value,
                y_label=y_label.value,
                nominal_value=float(nominal.value),
                min_limit=float(min_limit.value),
                max_limit=float(max_limit.value),
            )

            preview.set_source(
                image_path
            )

            preview.update()

            ui.notify(
                'Plot created',
                type='positive'
            )

        except Exception as e:

            logger.exception(e)

            ui.notify(
                str(e),
                type='negative'
            )

    with ui.row().classes(
        'w-full'
    ).style(
        'align-items:flex-start'
    ):

        #
        # Parameter
        #
        with ui.card().style(
            'width:350px;'
        ):

            ui.label(
                'DMM Plot'
            ).classes(
                'text-h6'
            )

            filename = ui.input(
                'Filename',
                value='PLOT'
            ).classes(
                'w-full'
            )

            title = ui.input(
                'Title'
            ).classes(
                'w-full'
            )

            y_label = ui.input(
                'Y Label',
                value='V'
            ).classes(
                'w-full'
            )

            samples = ui.number(
                'Samples',
                value=200
            ).classes(
                'w-full'
            )

            nominal = ui.number(
                'Nominal Value',
                value=5.0
            ).classes(
                'w-full'
            )

            min_limit = ui.number(
                'Min Limit',
                value=4.95
            ).classes(
                'w-full'
            )

            max_limit = ui.number(
                'Max Limit',
                value=5.05
            ).classes(
                'w-full'
            )

            ui.button(
                'Create Plot',
                on_click=create_plot
            ).classes(
                'w-full'
            )

        #
        # Preview
        #
        with ui.card().style(
            'flex:1;'
        ):

            ui.label(
                'Preview'
            ).classes(
                'text-h6'
            )

            preview = ui.image().classes(
                'w-full'
            )