from nicegui import ui
from gui.config import load_config, save_config

def build_configuration_page():

    cfg = load_config()

    devices = cfg["devices"]

    selected = cfg["selected"]

    with ui.card().style(
        'width:900px;'
    ):
        
        # ---------------------------
        # Header
        # ---------------------------

        ui.label("Device Configuration").classes("text-h6")

        ui.separator()

        # ---------------------------
        # Scope area
        # ---------------------------

        ui.label("Scope")

        scope_type = ui.select(
            list(devices["scope"].keys()),
            value = selected["scope"],
            label = "Type",
        ).classes("w-full")

        scope_resource = ui.input(
            label = "Resources",
            value = devices["scope"][selected["scope"]]["resource"]
        ).classes("w-full")

        def update_scope():

            scope_resource.value = (
                devices["scope"][scope_type.value]["resource"]
            )

        scope_type.on("update:model-value", lambda e: update_scope())

        ui.separator()

        # ---------------------------
        # DMM area
        # ---------------------------
        
        ui.label("DMM")

        dmm_type = ui.select(
            list(devices["dmm"].keys()),
            value=selected["dmm"],
            label="Type",
        ).classes("w-full")

        dmm_resource = ui.input(
            label = "Resource",
            value = devices["dmm"][selected["dmm"]]["resource"]
        ).classes("w-full")

        def update_dmm():

            dmm_resource.value = (
                devices["dmm"][dmm_type.value]["resource"]
            )

        dmm_type.on("update:model-value", lambda e: update_dmm())

        ui.separator()

        # ---------------------------
        # E-Load area
        # ---------------------------

        ui.label("Electronic Load")

        eload_type = ui.select(
            list(devices["eload"].keys()),
            value = selected["eload"],
            label = "Type",
        ).classes("w-full")

        eload_resource = ui.input(
            label = "Resource",
            value = devices["eload"][selected["eload"]]["resource"]
        ).classes("w-full")

        def update_eload():

            eload_resource.value = (
                devices["eload"][eload_type.value]["resource"]
            )

        eload_type.on("update:model-value", lambda e: update_eload())

        ui.separator()

        # ---------------------------
        # Save button
        # ---------------------------

        def save():

            cfg["selected"] = {

                "scope": {
                    "type": scope_type.value,
                },

                "dmm": {
                    "type": dmm_type.value,
                },

                "eload": {
                    "type": eload_type.value,
                }
            }

            cfg["devices"] = {

                "scope": {
                    "resource": scope_resource.value,
                },

                "dmm": {
                    "resource": dmm_resource.value,
                },

                "eload": {
                    "resource": eload_resource.value,
                }
            }

            save_config(cfg)

            ui.notify("Configuration saved", type="positive")

        ui.button("Save Configuration", on_click=save)