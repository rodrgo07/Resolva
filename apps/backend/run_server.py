import os
import sys
from pathlib import Path

# Adiciona o diretório do backend ao sys.path
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

os.environ["PYTHONUNBUFFERED"] = "1"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8700,
        log_level="info",
        access_log=True,
    )
