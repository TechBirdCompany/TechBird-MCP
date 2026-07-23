from collections import deque
from assets.theme import sizes, colors
from nicegui import ui

from gui.config import create_device, get_selected_device_config

def build_power_supply_widget():

    power_state = False
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

    card_height = 190

    with ui.row().classes(
        "w-full no-wrap items-stretch"
    ).style(
        "gap:12px;"
    ):

        # --------------------------------------------------
        # CONTROL CARD
        # --------------------------------------------------

        control_card_width = 350

        with ui.card().style(
            f"""
            width:{control_card_width}px;
            height:{card_height}px;
            padding:12px;
            """
        ):

            with ui.column().classes(
                "w-full h-full items-center"
            ):

                with ui.row().classes(
                    "items-center justify-between"
                ).style(
                    "width:300px;"
                ):

                    ui.label(
                        "USET"
                    ).style(
                        "width:100px;"
                    )

                    vset = ui.number(
                        value=24.0,
                        step=0.1,
                        format="%.1f",
                    ).props(
                        "dense outlined input-class=text-right"
                    ).style(
                        "width:100px;"
                    )

                    ui.label("V")

                with ui.row().classes(
                    "items-center justify-between"
                ).style(
                    "width:300px;"
                ):

                    ui.label(
                        "ISET"
                    ).style(
                        "width:100px;"
                    )

                    iset = ui.number(
                        value=2.0,
                        step=0.01,
                        format="%.2f",
                    ).props(
                        "dense outlined input-class=text-right"
                    ).style(
                        """
                        width:100px;
                        """
                    )

                    ui.label("A")

                ui.element("div").classes(
                    "flex-grow"
                )

                with ui.row().style(
                    """
                    width:300px;
                    gap:8px;
                    """
                ):
                    
                    connect_button = ui.button(
                        text = "CONNECT",
                        icon = "cable",
                        color = colors.ORANGE
                    ).props(
                        "dense"
                    ).style(
                        f"""
                        width:146px;
                        height:{sizes.BUTTON_HEIGHT}px;
                        """
                    )

                    apply_button = ui.button(
                        text = "APPLY",
                        icon = "save",
                        color = colors.BLUE
                    ).props(
                        "dense"
                    ).style(
                        f"""
                        width:146px;
                        height:{sizes.BUTTON_HEIGHT}px;
                        """
                    )

        # --------------------------------------------------
        # ACTUAL VALUES CARD
        # --------------------------------------------------

        with ui.card().style(
            f"""
            width:220px;
            height:{card_height}px;
            padding:12px;
            """
        ):

            with ui.column().classes(
                "w-full h-full"
            ):

                vact = ui.label(
                    "UOUT  0.000 V"
                ).style(
                    """
                    font-family:monospace;
                    font-size:16px;
                    """
                )

                iact = ui.label(
                    "IOUT  0.000 A"
                ).style(
                    """
                    font-family:monospace;
                    font-size:16px;
                    """
                )

                pact = ui.label(
                    "POUT  0.000 W"
                ).style(
                    """
                    font-family:monospace;
                    font-size:16px;
                    """
                )

                ui.element("div").classes(
                    "flex-grow"
                )

                power_button = ui.button(
                    text = "OFF",
                    icon = "power_settings_new",
                    color = colors.RED
                ).props(
                    f"""
                    dense
                    """
                ).style(
                    f"""
                    width:100%;
                    height:{sizes.BUTTON_HEIGHT}px;
                    """
                )

        # --------------------------------------------------
        # GRAPH CARD
        # --------------------------------------------------

        with ui.card().classes(
            "flex-grow"
        ).style(
            f"""
            height:{card_height}px;
            padding:8px;
            """
        ):

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
                    "data": list(range(120)),
                },

                "yAxis": [
                    {
                        "type": "value",
                        "name": "U [V]",
                        "splitLine": {
                            "show": False,
                        },
                        "nameTextStyle": {
                            "fontWeight": "bold",
                            "color": colors.BLUE,
                            "fontSize": 14,
                        },
                        "axisLabel": {
                            "color": colors.BLUE,
                            "fontWeight": "bold",
                        },
                    },
                    {
                        "type": "value",
                        "name": "I [A]",
                        "position": "right",
                        "splitLine": {
                            "show": False,
                        },
                        "nameTextStyle": {
                            "fontWeight": "bold",
                            "color": colors.RED,
                            "fontSize": 14,
                        },
                        "axisLabel": {
                            "color": colors.RED,
                            "fontWeight": "bold",
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
                        "data": list(voltage_history),
                        "color": colors.BLUE 
                    },
                    {
                        "name": "Current",
                        "type": "line",
                        "symbol": "none",
                        "smooth": True,
                        "yAxisIndex": 1,
                        "data": list(current_history),
                        "color": colors.RED,
                    },
                ],
            }).classes(
                "w-full"
            ).style(
                """
                width:100%
                height:100%;
                """
            )

    # --------------------------------------------------
    # Helper
    # --------------------------------------------------

    def reset_display():

        vact.set_text("UOUT  0.000 V")

        iact.set_text("IOUT  0.000 A")

        pact.set_text("POUT  0.000 W")

    # --------------------------------------------------
    # Device handling
    # --------------------------------------------------

    def connect():

        nonlocal ps

        try:

            device_cfg = get_selected_device_config("powersupply")

            ps = create_device(device_cfg)

            """
            try:
                ps.lock(True)
            except Exception:
                pass
            """
            
            ps.power_on_off("OFF")

            connect_button.set_text("CONNECTED")

            connect_button.style(
                f"""
                background: {colors.GREEN};
                color: white
                """
            )

            apply_values()
            
            connect_button.update()

            ui.notify(
                "Power supply connected",
                type="positive",
            )

        except Exception as ex:

            ps = None

            ui.notify(
                f"Connection failed: {ex}",
                type="negative",
            )

    def disconnect():

        nonlocal ps
        nonlocal power_state

        if ps is None:
            return

        try:

            try:
                ps.power_on_off("OFF")
            except Exception:
                pass

            try:
                ps.close()
            except Exception:
                pass

        finally:

            ps = None
            power_state = False

            power_button.set_text("OFF")
            
            power_button.style(
                f"""
                background: {colors.RED};
                color: white
                """
            )

            power_button.update()

            connect_button.set_text("DISCONNECTED")

            connect_button.style(
                f"""
                background: {colors.ORANGE};
                color: white
                """
            )           

            connect_button.update()

            reset_display()

            ui.notify(
                "Disconnected",
                type="info",
            )

    def connect_toggle():

        if ps is None:
            connect()
        else:
            disconnect()

    # --------------------------------------------------
    # Actions
    # --------------------------------------------------

    def apply_values():

        if ps is None:

            ui.notify(
                "Not connected",
                type="warning",
            )

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

        if ps is None:

            ui.notify(
                "Not connected",
                type="warning",
            )

            return

        try:

            if power_button.text == "ON":
                ps.power_on_off("OFF")
            else:
                ps.power_on_off("ON")

        except Exception as ex:

            ui.notify(
                str(ex),
                type="negative",
            )

    def update_power_button(voltage: float):

        target_voltage = float(vset.value)

        tolerance = target_voltage * 0.03  # 3 %

        is_on = abs(voltage - target_voltage) <= tolerance

        if is_on:
  
            power_button.set_text("ON")

            power_button.style(
                f"""
                background: {colors.GREEN};
                color: white;
                """
            )

        else:

            power_button.set_text("OFF")

            power_button.style(
                f"""
                background: {colors.RED};
                color: white;
                """
            )

        power_button.update()

    apply_button.on(
        "click",
        apply_values,
    )

    connect_button.on(
        "click",
        connect_toggle,
    )

    power_button.on(
        "click",
        power_changed,
    )

    # --------------------------------------------------
    # Update
    # --------------------------------------------------

    def update():

        nonlocal ps

        if ps is None:
            return

        try:

            voltage, current = (ps.get_value())

            update_power_button(voltage)

            power = (voltage * current)

            vact.set_text(f"UOUT {voltage:>6.3f} V")

            iact.set_text(f"IOUT {current:>6.3f} A")

            pact.set_text(f"POUT {power:>6.3f} W")

            voltage_history.append(voltage)

            current_history.append(current)

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

            disconnect()

    ui.timer(
        0.05,
        update,
    )