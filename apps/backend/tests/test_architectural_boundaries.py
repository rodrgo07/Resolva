import os
import sys
import pytest
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
BACKEND_DIR = ROOT_DIR / "apps" / "backend"
DESKTOP_DIR = ROOT_DIR / "apps" / "desktop"
MOBILE_DIR = ROOT_DIR / "apps" / "mobile"

def test_backend_does_not_import_frontend_or_mobile():
    backend_py_files = list(BACKEND_DIR.glob("**/*.py"))
    forbidden_imports = ["react", "react-native", "expo", "desktop", "mobile", "window", "document"]
    
    for py_file in backend_py_files:
        if ".venv" in str(py_file) or "__pycache__" in str(py_file):
            continue
        content = py_file.read_text(encoding="utf-8", errors="ignore").lower()
        for forbidden in forbidden_imports:
            assert f"import {forbidden}" not in content, f"Forbidden import '{forbidden}' in {py_file}"
            assert f"from {forbidden}" not in content, f"Forbidden from import '{forbidden}' in {py_file}"

def test_frontend_does_not_import_backend_python_or_sqlite():
    desktop_files = list((DESKTOP_DIR / "src").glob("**/*.ts*"))
    mobile_files = list((MOBILE_DIR / "src").glob("**/*.ts*"))
    
    forbidden_patterns = [
        "import * as sqlite3", "from 'sqlite3'", "from 'better-sqlite3'",
        "from 'sqlalchemy'", "import app.models", ".db"
    ]
    
    for f in desktop_files + mobile_files:
        content = f.read_text(encoding="utf-8", errors="ignore")
        for pat in forbidden_patterns:
            if pat == ".db" and "api/system" in content:
                continue # ignore api strings
            assert pat not in content, f"Frontend directly importing backend/database pattern '{pat}' in {f}"

def test_frontend_and_mobile_have_no_hardcoded_secrets():
    ts_files = list((DESKTOP_DIR / "src").glob("**/*.ts*")) + list((MOBILE_DIR / "src").glob("**/*.ts*"))
    
    for f in ts_files:
        content = f.read_text(encoding="utf-8", errors="ignore")
        assert "insecure_dev_key" not in content, f"SECRET_KEY leaked in frontend file {f}"
        assert "change-this-to-a-random-secret-key" not in content, f"SECRET_KEY leaked in frontend file {f}"
