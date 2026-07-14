from pathlib import Path
import yaml
from gui.device_registry import DEVICE_INFO

CONFIG_FILE = Path(
    "config/devices.yaml"
)

def load_config():

    if not CONFIG_FILE.exists():

        raise FileNotFoundError(f"Missing configuration file: {CONFIG_FILE}")

    with open(CONFIG_FILE, "r", encoding="utf-8") as file:
        
        return yaml.safe_load(file)

def save_config(config):

    CONFIG_FILE.parent.mkdir(exist_ok = True)

    with open(CONFIG_FILE, "w", encoding="utf-8") as file:
        
        yaml.safe_dump(config, file, sort_keys=False)

def create_device(device_cfg):

    device_class = DEVICE_INFO[device_cfg["type"]]["class"]

    resource = device_cfg["resource"]

    if resource == "AUTO":

        if hasattr(device_class, "auto_connect"):
            
            return device_class.auto_connect()

        return device_class()

    return device_class(resource)

def get_selected_device_name(category):
    config = load_config()
    return config["selected"][category]


def get_selected_device_config(category):
    config = load_config()

    device_name = config["selected"][category]

    return config["devices"][category][device_name]


def get_selected_resource(category):
    device_cfg = get_selected_device_config(category)
    return device_cfg.get("resource")


def set_selected_device(category, device_name):
    config = load_config()

    if device_name not in config["devices"]:raise ValueError(
            f"Unknown device '{device_name}' for category '{category}'"
        )

    config["selected"][category] = device_name

    save_config(config)
