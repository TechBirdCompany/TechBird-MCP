from nicegui import ui

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

        # ---------------------------
        # Scope area
        # ---------------------------

        ui.label("Scope")

        scope_type = ui.select(
            options=list(devices["scope"].keys()),
            value=selected["scope"],
            label="Type",
        ).classes("w-full")

        scope_resource = ui.input(
            label="Resource",
            value=devices["scope"][selected["scope"]].get("resource", ""),
        ).classes("w-full")

        scope_type.on(
            "update:model-value",
            lambda e: reload_from_config(),
        )

        ui.separator()

        # ---------------------------
        # DMM area
        # ---------------------------

        ui.label("DMM")

        dmm_type = ui.select(
            options=list(devices["dmm"].keys()),
            value=selected["dmm"],
            label="Type",
        ).classes("w-full")

        dmm_resource = ui.input(
            label="Resource",
            value=devices["dmm"][selected["dmm"]].get("resource", ""),
        ).classes("w-full")

        dmm_type.on(
            "update:model-value",
            lambda e: reload_from_config(),
        )

        ui.separator()

        # ---------------------------
        # E-Load area
        # ---------------------------

        ui.label("Electronic Load")

        eload_type = ui.select(
            options=list(devices["eload"].keys()),
            value=selected["eload"],
            label="Type",
        ).classes("w-full")

        eload_resource = ui.input(
            label="Resource",
            value=devices["eload"][selected["eload"]].get("resource", ""),
        ).classes("w-full")

        eload_type.on(
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

            save_config(cfg)

            ui.notify(
                "Configuration saved",
                type="positive",
            )

        ui.button(
            "Save Configuration",
            on_click=save,
        )