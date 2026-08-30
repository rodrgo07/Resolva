import os
import json
import uuid
from pathlib import Path

def get_appdata_dir() -> Path:
    appdata = os.getenv("APPDATA")
    if not appdata:
        appdata = str(Path.home() / ".resolva")
    base_dir = Path(appdata) / "Resolva"
    base_dir.mkdir(parents=True, exist_ok=True)
    return base_dir

def get_backups_dir() -> Path:
    b_dir = get_appdata_dir() / "backups"
    b_dir.mkdir(parents=True, exist_ok=True)
    return b_dir

def get_or_create_device_id() -> str:
    """
    Retorna ou inicializa o identificador único e anônimo da instalação persistido em %APPDATA%/Resolva/device.json
    """
    device_file = get_appdata_dir() / "device.json"
    if device_file.exists():
        try:
            data = json.loads(device_file.read_text(encoding="utf-8"))
            if "device_id" in data:
                return data["device_id"]
        except Exception:
            pass

    new_id = f"device_{uuid.uuid4().hex[:16]}"
    device_file.write_text(json.dumps({"device_id": new_id, "created_at": str(uuid.uuid1())}), encoding="utf-8")
    return new_id
