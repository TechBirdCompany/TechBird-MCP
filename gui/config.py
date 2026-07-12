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
