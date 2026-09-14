from nicegui import ui
from loguru import logger
import threading
from pathlib import Path
import yaml
from assets.theme import sizes, colors

from gui.config import (
    load_config,
    create_device,
    get_selected_device_config,
)

from tools.test_load import test_load

CONFIG_FILE = (
    Path(__file__).resolve().parents[2]
    / "config"
    / "load_test.yaml"
)

DEFAULT_CONFIG = {
    "domain": "VCC_5V0",
    "voltage": 5.0,
    "min_voltage": 4.95,
    "max_voltage": 5.05,
    "current": 0.5,
    "samples": 200,
    "single": False,
    "current_probe_attenuation": 10.0,
    "dc_sec_per_div": 1e-3,
    "ac_sec_per_div": 0.1e-3,
    "ac_voltage_percentage": 0.075,
    "advanced": False,
    "advanced_dc_sec_per_div": 1e-3,
    "advanced_ac_sec_per_div": 0.1e-3,
    "advanced_ac_volts_per_div": 0.05,
}

def load_page_config():
    if not CONFIG_FILE.exists():
        save_page_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f) or {}

        result = DEFAULT_CONFIG.copy()
        result.update(cfg)

        if "ac_volts_per_div" in cfg and "advanced_ac_volts_per_div" not in cfg:
            result["advanced_ac_volts_per_div"] = cfg["ac_volts_per_div"]

        for key in [
            "voltage",
            "min_voltage",
            "max_voltage",
            "current",
            "current_probe_attenuation",
            "dc_sec_per_div",
            "ac_sec_per_div",
            "ac_voltage_percentage",
            "advanced_dc_sec_per_div",
            "advanced_ac_sec_per_div",
            "advanced_ac_volts_per_div",
        ]:
            if key in result and result[key] is not None:
                result[key] = float(result[key])

        if "samples" in result and result["samples"] is not None:
            result["samples"] = int(result["samples"])

        return result

    except Exception as e:
        logger.exception(e)
        return DEFAULT_CONFIG.copy()

def save_page_config(config):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        yaml.safe_dump(
            config,
            f,
            sort_keys=False,
            allow_unicode=True,
        )

def build_load_test_page():

    page_cfg = load_page_config()

    test_results = []
    last_result_count = 0

    test_finished = False
    test_error = None

    gallery = None
    dialog = None
    preview = None

    def get_current_values():
        return {
            "domain": domain.value,
            "voltage": float(voltage.value),
            "min_voltage": float(min_voltage.value),
            "max_voltage": float(max_voltage.value),
            "current": float(current.value),
            "samples": int(samples.value),
            "single": bool(single.value),
            "current_probe_attenuation": float(current_probe_attenuation.value),
            "dc_sec_per_div": float(dc_sec_per_div.value),
            "ac_sec_per_div": float(ac_sec_per_div.value),
            "ac_voltage_percentage": float(page_cfg.get("ac_voltage_percentage", 0.075)),
            "advanced": bool(advanced.value),
            "advanced_dc_sec_per_div": float(advanced_dc_sec_per_div.value),
            "advanced_ac_sec_per_div": float(advanced_ac_sec_per_div.value),
            "advanced_ac_volts_per_div": float(advanced_ac_volts_per_div.value),
        }

    def persist():
        try:
            save_page_config(get_current_values())
        except Exception as e:
            logger.exception(e)

    def on_advanced_change():

        single.value = advanced.value   # Advanced measurments are always single measurments

        persist()

    def open_preview(image_path):

        preview.set_source(image_path)
        preview.update()

        dialog.open()

    def show_results(files):

        gallery.clear()

        with gallery:

            for file in files[:9]:

                image_path = file.replace("\\", "/")

                image = ui.image(
                    image_path
                ).style(
                    """
                    width:350px;
                    height:auto;
                    cursor:pointer;
                    margin:auto;
                    """
                )

                image.tooltip(image_path.split("/")[-1])

                image.on(
                    "click",
                    lambda e, p=image_path: open_preview(p)
                )

    def check_for_results():

        nonlocal test_results
        nonlocal last_result_count
        nonlocal test_finished
        nonlocal test_error

        if test_finished:

            ui.notify(
                "Load Test completed",
                type="positive"
            )

            test_finished = False

        if test_error:

            ui.notify(
                test_error,
                type="negative"
            )

            test_error = None

        if not test_results:
            return

        if len(test_results) == last_result_count:
            return

        last_result_count = len(test_results)

        show_results(test_results)

    def run_load_test():

        nonlocal test_results
        nonlocal last_result_count
        nonlocal test_finished
        nonlocal test_error

        test_results = []
        last_result_count = 0
        test_finished = False
        test_error = None

        try:

            persist()

            scope = create_device(
                get_selected_device_config("scope")
            )

            dmm = create_device(
                get_selected_device_config("dmm")
            )

            eload = create_device(
                get_selected_device_config("eload")
            )

            test_results = test_load(
                scope=scope,
                dmm=dmm,
                eload=eload,
                voltage=float(voltage.value),
                max_voltage=float(max_voltage.value),
                min_voltage=float(min_voltage.value),
                domain=domain.value,
                current=float(current.value),
                samples=int(samples.value),
                single=single.value,
                current_probe_attenuation=float(current_probe_attenuation.value),
                dc_sec_per_div=float(dc_sec_per_div.value),
                ac_sec_per_div=float(ac_sec_per_div.value),
                ac_voltage_percentage=float(page_cfg.get("ac_voltage_percentage", 0.075)),
                advanced=bool(advanced.value),
                advanced_dc_sec_per_div=float(advanced_dc_sec_per_div.value),
                advanced_ac_sec_per_div=float(advanced_ac_sec_per_div.value),
                advanced_ac_volts_per_div=float(advanced_ac_volts_per_div.value),
            )

            logger.info("Load Test completed")

            test_finished = True

        except Exception as e:

            logger.exception(e)

            test_error = str(e)

    with ui.row().classes("w-full").style("align-items:flex-start"):

        with ui.card().style("width:350px;"):

            ui.label("Load Test").classes("text-h6")

            domain = (
                ui.input(
                    "Domain",
                    value=page_cfg["domain"]
                )
                .classes("w-full")
                .on("change", lambda e: persist())
            )

            voltage = (
                ui.number(
                    "Voltage",
                    value=page_cfg["voltage"]
                )
                .classes("w-full")
                .on("change", lambda e: persist())
            )

            min_voltage = (
                ui.number(
                    "Min Voltage",
                    value=page_cfg["min_voltage"]
                )
                .classes("w-full")
                .on("change", lambda e: persist())
            )

            max_voltage = (
                ui.number(
                    "Max Voltage",
                    value=page_cfg["max_voltage"]
                )
                .classes("w-full")
                .on("change", lambda e: persist())
            )

            current = (
                ui.number(
                    "Current",
                    value=page_cfg["current"]
                )
                .classes("w-full")
                .on("change", lambda e: persist())
            )

            samples = (
                ui.number(
                    "Samples",
                    value=page_cfg["samples"]
                )
                .classes("w-full")
                .on("change", lambda e: persist())
            )

            current_probe_attenuation = (
                ui.number(
                    "Current Probe Attenuation",
                    value=page_cfg["current_probe_attenuation"]
                )
                .classes("w-full")
                .on("change", lambda e: persist())
            )

            dc_sec_per_div = (
                ui.number(
                    "DC Timebase [s/div]",
                    value=page_cfg["dc_sec_per_div"],
                    format="%g",
                )
                .classes("w-full")
                .on("change", lambda e: persist())
            )

            ac_sec_per_div = (
                ui.number(
                    "AC Timebase [s/div]",
                    value=page_cfg["ac_sec_per_div"],
                    format="%g",
                )
                .classes("w-full")
                .on("change", lambda e: persist())
            )

            single = ui.checkbox(
                "Single Measurement",
                value=page_cfg["single"],
                on_change=lambda e: persist(),
            )

            advanced = ui.checkbox(
                "Advanced",
                value=page_cfg["advanced"],
                on_change=lambda e: on_advanced_change(),
            )

            single.bind_enabled_from(  # Advanced measurments are always single measurments
                advanced,
                "value",
                backward=lambda value: not value,
            )

            if advanced.value:
                single.value = True

            with ui.column().classes("w-full").bind_visibility_from(
                advanced, "value"
            ):

                advanced_dc_sec_per_div = (
                    ui.number(
                        "Advanced DC Timebase [s/div]",
                        value=page_cfg.get("advanced_dc_sec_per_div", page_cfg["dc_sec_per_div"]),
                        format="%g",
                    )
                    .classes("w-full")
                    .on("change", lambda e: persist())
                )

                advanced_ac_sec_per_div = (
                    ui.number(
                        "Advanced AC Timebase [s/div]",
                        value=page_cfg.get("advanced_ac_sec_per_div", page_cfg["ac_sec_per_div"]),
                        format="%g",
                    )
                    .classes("w-full")
                    .on("change", lambda e: persist())
                )

                advanced_ac_volts_per_div = (
                    ui.number(
                        "Advanced AC Volts per Division [V/div]",
                        value=page_cfg.get("advanced_ac_volts_per_div", page_cfg.get("ac_volts_per_div", 0.05)),
                        format="%g",
                    )
                    .classes("w-full")
                    .on("change", lambda e: persist())
                )

            ui.button(
                text = "Start Load Test",
                on_click = lambda: threading.Thread(
                    target=run_load_test,
                    daemon=True,
                ).start(),
                color = colors.GENERAL_BUTTON
            ).classes("w-full")

        with ui.card().style("flex:1;"):

            ui.label(
                "Generated Files"
            ).classes("text-h6")

            dialog = ui.dialog().props(
                "maximized"
            )

            with dialog:

                preview = ui.image().style(
                    """
                    max-width:80vw;
                    max-height:80vh;
                    object-fit:contain;
                    """
                )

            gallery = (
                ui.grid(columns=3)
                .classes("w-full")
                .style(
                    "justify-items:center;"
                )
            )

    ui.timer(1.0, check_for_results)