from nicegui import ui
from assets.theme import sizes, colors

from gui.config import load_config, save_config


def build_configuration_page():

    cfg = load_config()

    devices = cfg["devices"]
    selected = cfg["selected"]

    with ui.card().style("width:900px;"):

        # ---------------------------
        # Header
        # ---------------------------

        ui.label("Device Configuration").classes("text-h6")

        ui.separator()

        # ---------------------------
        # Helper
        # ---------------------------

        def update_resource(category, select_widget, resource_widget):

            resource_widget.value = (
                devices[category][select_widget.value]
                .get("resource", "")
            )
    
        def reload_from_config():

            cfg = load_config()

            devices = cfg["devices"]

            scope_resource.value = (
                devices["scope"][scope_type.value]
                .get("resource", "")
            )

            dmm_resource.value = (
                devices["dmm"][dmm_type.value]
                .get("resource", "")
            )

            eload_resource.value = (
                devices["eload"][eload_type.value]
                .get("resource", "")
            )

            powersupply_resource.value = (
                devices["powersupply"][powersupply_type.value]
                .get("resource", "")
            )

        # ---------------------------
        # Scope area
        # ---------------------------

        with ui.row().classes(
            "w-full h-full"
        ):

            ui.label(
                text = "Scope"
            ).style(
                "width:120px"
            )

            scope_type = ui.select(
                options=list(devices["scope"].keys()),
                value=selected["scope"],
                label="Type",
            ).style("width:250px")

            scope_resource = ui.input(
                label="Resource",
                value=devices["scope"][selected["scope"]].get("resource", ""),
            ).classes("flex-grow")

            scope_type.on(
                "update:model-value",
                lambda e: reload_from_config(),
            )

        ui.separator()

        # ---------------------------
        # DMM area
        # ---------------------------

        with ui.row().classes(
            "w-full h-full"
        ):

            ui.label(
                text = "DMM"
            ).style(
                "width:120px"
            )

            dmm_type = ui.select(
                options=list(devices["dmm"].keys()),
                value=selected["dmm"],
                label="Type",
            ).style("width:250px")

            dmm_resource = ui.input(
                label="Resource",
                value=devices["dmm"][selected["dmm"]].get("resource", ""),
            ).classes("flex-grow")

            dmm_type.on(
                "update:model-value",
                lambda e: reload_from_config(),
            )

        ui.separator()

        # ---------------------------
        # E-Load area
        # ---------------------------

        with ui.row().classes(
            "w-full h-full"
        ):

            ui.label(
                text = "Electronic Load"
            ).style(
                "width:120px"
            )

            eload_type = ui.select(
                options=list(devices["eload"].keys()),
                value=selected["eload"],
                label="Type",
            ).style("width:250px")

            eload_resource = ui.input(
                label="Resource",
                value=devices["eload"][selected["eload"]].get("resource", ""),
            ).classes("flex-grow")

            eload_type.on(
                "update:model-value",
                lambda e: reload_from_config(),
            )

        ui.separator()

        # ---------------------------
        # Power Supply area
        # ---------------------------

        with ui.row().classes(
            "w-full h-full"
        ):

            ui.label(
                text = "Power Supply"
            ).style(
                "width:120px"
            )

            powersupply_type = ui.select(
                options=list(devices["powersupply"].keys()),
                value=selected["powersupply"],
                label="Type",
            ).style("width:250px")

            powersupply_resource = ui.input(
                label="Resource",
                value=devices["powersupply"][selected["powersupply"]].get("resource", ""),
            ).classes("flex-grow")

            powersupply_type.on(
                "update:model-value",
                lambda e: reload_from_config(),
            )

        ui.separator()

        # ---------------------------
        # Save button
        # ---------------------------

        def save():

            # aktuell ausgewählte Geräte speichern
            cfg["selected"]["scope"] = scope_type.value
            cfg["selected"]["dmm"] = dmm_type.value
            cfg["selected"]["eload"] = eload_type.value
            cfg["selected"]["powersupply"] = powersupply_type.value

            # Ressourcen des ausgewählten Geräts speichern
            cfg["devices"]["scope"][scope_type.value]["resource"] = (
                scope_resource.value
            )

            cfg["devices"]["dmm"][dmm_type.value]["resource"] = (
                dmm_resource.value
            )

            cfg["devices"]["eload"][eload_type.value]["resource"] = (
                eload_resource.value
            )

            cfg["devices"]["powersupply"][powersupply_type.value]["resource"] = (
                powersupply_resource.value
            )

            save_config(cfg)

            ui.notify(
                "Configuration saved",
                type="positive",
            )

        ui.button(
            text = "Save Configuration",
            on_click=save,
            color = colors.GENERAL_BUTTON
        )