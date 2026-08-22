from pathlib import Path
import yaml

from nicegui import ui
from loguru import logger
from assets.theme import sizes, colors

from gui.config import load_config, create_device, get_selected_device_config
from tools.get_visual import get_screenshot_scope

ROOT_DIR = Path(__file__).resolve().parents[2]

CONFIG_DIR = ROOT_DIR / "config"
CONFIG_FILE = CONFIG_DIR / "scope_screenshot.yaml"

DEFAULT_CONFIG = {
    "filename": "SCOPE",
    "ch1": "",
    "ch2": "",
    "ch3": "",
    "ch4": "",
}

def load_page_config():
    CONFIG_DIR.mkdir(exist_ok=True)

    if not CONFIG_FILE.exists():
        save_page_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f) or {}

        result = DEFAULT_CONFIG.copy()
        result.update(cfg)

        return result

    except Exception as e:
        logger.exception(e)
        return DEFAULT_CONFIG.copy()


def save_page_config(config):
    CONFIG_DIR.mkdir(exist_ok=True)

    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        yaml.safe_dump(
            config,
            f,
            sort_keys=False,
            allow_unicode=True,
        )


def build_scope_screenshot_page():

    page_cfg = load_page_config()

    preview = None

    def get_current_values():
        return {
            "filename": filename.value,
            "ch1": ch1.value,
            "ch2": ch2.value,
            "ch3": ch3.value,
            "ch4": ch4.value,
        }

    def persist():
        try:
            save_page_config(get_current_values())
        except Exception as e:
            logger.exception(e)

    def create_screenshot():

        try:

            persist()

            cfg = load_config()

            scope = create_device(
                get_selected_device_config("scope")
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

            ui.notify(
                "Screenshot created",
                type="positive"
            )

        except Exception as e:

            logger.exception(e)

            ui.notify(
                str(e),
                type="negative"
            )

    def remove_labels():
        scope = create_device(
            get_selected_device_config("scope")
        )

        for i in range(4):
            scope.set_label(i + 1, "")

    with ui.row().classes("w-full").style("align-items:flex-start"):

        with ui.card().style("width:350px;"):

            ui.label(
                "Parameters"
            ).classes("text-h6")

            filename = (
                ui.input(
                    "Filename",
                    value=page_cfg["filename"]
                )
                .classes("w-full")
                .on("change", lambda e: persist())
            )

            ch1 = (
                ui.input(
                    "CH1 Label",
                    value=page_cfg["ch1"]
                )
                .classes("w-full")
                .on("change", lambda e: persist())
            )

            ch2 = (
                ui.input(
                    "CH2 Label",
                    value=page_cfg["ch2"]
                )
                .classes("w-full")
                .on("change", lambda e: persist())
            )

            ch3 = (
                ui.input(
                    "CH3 Label",
                    value=page_cfg["ch3"]
                )
                .classes("w-full")
                .on("change", lambda e: persist())
            )

            ch4 = (
                ui.input(
                    "CH4 Label",
                    value=page_cfg["ch4"]
                )
                .classes("w-full")
                .on("change", lambda e: persist())
            )

            ui.button(
                text = "Remove Labels",
                on_click = remove_labels,
                color = colors.ORANGE
            ).classes(
                "w-full"
            )

            ui.button(
                text = "Create Screenshot",
                on_click = create_screenshot,
                color = colors.GENERAL_BUTTON
            ).classes(
                "w-full"
            )

        with ui.card().style(
            """
            flex:1;
            display:flex;
            justify-content:center;
            align-items:center;
            """
        ):

            preview = ui.image().style(
                """
                width:1024px;
                max-width:90%;
                border:1px solid #444;
                """
            )