from collections import deque

from nicegui import ui

from gui.config import (
    create_device,
    get_selected_device_config,
)


def build_power_supply_widget():

    power_state = False

    # --------------------------------------------------
    # Connect PSU
    # --------------------------------------------------

    try:

        device_cfg = get_selected_device_config(
            "powersupply"
        )

        ps = create_device(device_cfg)

        try:
            ps.lock(True)
        except Exception:
            pass

    except Exception as ex:

        print(
            f"PSU connect failed: {ex}"
        )

        ps = None

    # --------------------------------------------------
    # History
    # --------------------------------------------------

    voltage_history = deque(
        [0.0] * 120,
        maxlen=120,
    )

    current_history = deque(
        [0.0] * 120,
        maxlen=120,
    )

    # --------------------------------------------------
    # Layout
    # --------------------------------------------------

    with ui.row().classes(
        "flex-grow no-wrap items-start"
    ).style(
        "column-gap: 20px;"
    ):

        # ----------------------------------------------
        # Controls
        # ----------------------------------------------

        with ui.column().style(
            """
            width:180px;
            min-width:180px;
            """
        ):

            with ui.row().classes("items-center"):

                ui.label("USET").style("width:50px")

                vset = ui.number(
                    value=12.0,
                    step=0.1,
                    format="%.1f",
                ).props(
                    "dense outlined input-class=text-right"
                ).style(
                    """
                    width:80px;
                    """
                )

                ui.label(" V")

            with ui.row().classes("items-center"):

                ui.label("ISET").style("width:50px")

                iset = ui.number(
                    value=1.0,
                    step=0.01,
                    format="%.2f",
                ).props(
                    "dense outlined input-class=text-right"
                ).style(
                    """
                    width:80px;
                    """
                )

                ui.label(" A")

            with ui.row().classes(
                "w-full justify-center"
            ):

                apply_button = ui.button(
                    "APPLY"
                ).props(
                    "dense"
                ).style(
                    """
                    width:70px;
                    """
                )

                power_button = ui.button(
                    "OFF",
                    color="red",
                ).props(
                    "dense"
                ).style(
                    """
                    width:70px;
                    """
                )



        with ui.card().style(
            """
            width:200px;
            padding:10px;
            """
        ):

            with ui.column().classes("w-full"):

                vact = ui.label(
                    "U   0.00 V"
                ).style(
                    """
                    font-family:monospace;
                    font-size:16px;
                    """
                )

                iact = ui.label(
                    "I   0.000 A"
                ).style(
                    """
                    font-family:monospace;
                    font-size:16px;
                    """
                )

                pact = ui.label(
                    "P   0.00 W"
                ).style(
                    """
                    font-family:monospace;
                    font-size:16px;
                    """
                )


        # ----------------------------------------------
        # Graph
        # ----------------------------------------------

        graph = ui.echart({

            "animation": False,

            "grid": {
                "left": 5,
                "right": 5,
                "top": 5,
                "bottom": 5,
            },

            "xAxis": {
                "type": "category",
                "show": False,
                "data": list(
                    range(120)
                ),
            },

            "yAxis": [
                {
                    "type": "value",
                    "name": "U [V]",
                    "position": "left",
                    "splitLine": {
                        "show": True,
                    },
                },
                {
                    "type": "value",
                    "name": "I [A]",
                    "position": "right",
                    "splitLine": {
                        "show": False,
                    },
                },
            ],

            "series": [

                {
                    "name": "Voltage",
                    "type": "line",
                    "symbol": "none",
                    "smooth": True,
                    "yAxisIndex": 0,
                    "data": list(
                        voltage_history
                    ),
                    "lineStyle": {
                        "width": 2,
                        "color": "#1976D2",
                    },
                },

                {
                    "name": "Current",
                    "type": "line",
                    "symbol": "none",
                    "smooth": True,
                    "yAxisIndex": 1,
                    "data": list(
                        current_history
                    ),
                    "lineStyle": {
                        "width": 2,
                        "color": "#D32F2F",
                    },
                },
            ],
        }).classes(
            "flex-grow"
        ).style(
            """
            height:160px;
            """
        )

    # --------------------------------------------------
    # Actions
    # --------------------------------------------------

    def apply_values():

        if ps is None:
            return

        try:

            ps.set_values(
                voltage=float(vset.value),
                current=float(iset.value),
            )

            ui.notify(
                "Values applied",
                type="positive",
            )

        except Exception as ex:

            ui.notify(
                str(ex),
                type="negative",
            )

    def power_changed():

        nonlocal power_state

        if ps is None:
            return

        try:

            power_state = not power_state

            if power_state:

                ps.power_on_off(
                    "ON"
                )

                power_button.set_text(
                    "ON"
                )

                power_button.props(
                    "color=green"
                )

            else:

                ps.power_on_off(
                    "OFF"
                )

                power_button.set_text(
                    "OFF"
                )

                power_button.props(
                    "color=red"
                )

            power_button.update()

        except Exception as ex:

            ui.notify(
                str(ex),
                type="negative",
            )

    apply_button.on(
        "click",
        apply_values,
    )

    power_button.on(
        "click",
        power_changed,
    )

    # --------------------------------------------------
    # Update
    # --------------------------------------------------

    def update():

        if ps is None:
            return

        try:

            voltage, current = (
                ps.get_value()
            )

            power = (
                voltage * current
            )

            vact.set_text(
                f"UOUT {voltage:>6.3f} V"
            )

            iact.set_text(
                f"IOUT {current:>6.3f} A"
            )

            pact.set_text(
                f"POUT {power:>6.3f} W"
            )

            voltage_history.append(
                voltage
            )

            current_history.append(
                current
            )

            graph.options[
                "series"
            ][0]["data"] = list(
                voltage_history
            )

            graph.options[
                "series"
            ][1]["data"] = list(
                current_history
            )

            graph.update()

        except Exception:
            pass

    ui.timer(
        0.2,
        update,
    )