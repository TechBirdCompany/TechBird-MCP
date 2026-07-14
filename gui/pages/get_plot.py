from nicegui import ui
from loguru import logger

from gui.config import load_config, create_device
from tools.get_visual import get_plot_dmm

from pathlib import Path
import yaml


CONFIG_FILE = (
    Path(__file__).resolve().parents[2]
    / "config"
    / "get_plot.yaml"
)

DEFAULT_CONFIG = {
    "filename": "DMM",
    "title": "",
    "y_label": "V",
    "samples": 200,
    "nominal": 5.0,
    "min_limit": 4.95,
    "max_limit": 5.05,
}

def load_plot_config():
    if not CONFIG_FILE.exists():
        save_plot_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()

    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or DEFAULT_CONFIG.copy()


def save_plot_config(cfg):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        yaml.safe_dump(cfg, f, sort_keys=False)


def build_get_plot_page():

    cfg_plot = load_plot_config()

    preview = None

    def get_current_values():
        return {
            "filename": filename.value,
            "title": title.value,
            "y_label": y_label.value,
            "samples": int(samples.value),
            "nominal": float(nominal.value),
            "min_limit": float(min_limit.value),
            "max_limit": float(max_limit.value),
        }

    def persist():
        save_plot_config(get_current_values())

    def create_plot():

        try:
            persist()

            cfg = load_config()

            dmm = create_device(cfg["selected"]["dmm"])

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

            preview.set_source(image_path)
            preview.update()

            ui.notify("Plot created", type="positive")

        except Exception as e:
            logger.exception(e)
            ui.notify(str(e), type="negative")

    with ui.row().classes("w-full").style("align-items:flex-start"):

        with ui.card().style("width:350px;"):

            ui.label("DMM Plot").classes("text-h6")

            filename = ui.input(
                "Filename",
                value=cfg_plot["filename"]
            ).classes("w-full").on("change", lambda e: persist())

            title = ui.input(
                "Title",
                value=cfg_plot["title"]
            ).classes("w-full").on("change", lambda e: persist())

            y_label = ui.input(
                "Y Label",
                value=cfg_plot["y_label"]
            ).classes("w-full").on("change", lambda e: persist())

            samples = ui.number(
                "Samples",
                value=cfg_plot["samples"]
            ).classes("w-full").on("change", lambda e: persist())

            nominal = ui.number(
                "Nominal Value",
                value=cfg_plot["nominal"]
            ).classes("w-full").on("change", lambda e: persist())

            min_limit = ui.number(
                "Min Limit",
                value=cfg_plot["min_limit"]
            ).classes("w-full").on("change", lambda e: persist())

            max_limit = ui.number(
                "Max Limit",
                value=cfg_plot["max_limit"]
            ).classes("w-full").on("change", lambda e: persist())

            ui.button(
                "Create Plot",
                on_click=create_plot
            ).classes("w-full")

        with ui.card().style("flex:1;"):

            ui.label("Preview").classes("text-h6")

            preview = ui.image().classes("w-full")