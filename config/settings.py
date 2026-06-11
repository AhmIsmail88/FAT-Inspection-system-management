"""
HAC FAT & Inspection Management System
Designed by Ahmed Hassanin
"""

import os
import sys
import json
from pathlib import Path

# ─── App Identity ─────────────────────────────────────────────────────────────
APP_NAME     = "HAC FAT & Inspection System"
APP_VERSION  = "1.0.0"
COMPANY_NAME = "HAC"
DESIGNED_BY  = "Designed By: Ahmed Hassanin"
FOOTER_TEXT  = "لا تنسونا من صالح الدعاء"

# ─── Local config folder (always on user's machine) ───────────────────────────
LOCAL_BASE   = Path(os.path.expanduser("~")) / "FATSystem"
CONFIG_FILE  = LOCAL_BASE / "config.json"

# ─── Default server path ──────────────────────────────────────────────────────
DEFAULT_SERVER_PATH = Path(r"V:\Fat Test (Infra - HUB)\DB")

# ─── Config read / write ──────────────────────────────────────────────────────

def read_config() -> dict:
    """Read config.json from local folder. Returns {} if not found."""
    try:
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return {}


def write_config(data: dict) -> None:
    """Write (merge) data into config.json."""
    LOCAL_BASE.mkdir(parents=True, exist_ok=True)
    existing = read_config()
    existing.update(data)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=2, ensure_ascii=False)


def get_db_base_path() -> Path:
    """
    Path resolution order:
      1. User-defined path from config.json  (if dir is accessible)
      2. Default server path                 (if accessible)
      3. Local ~/FATSystem fallback
    """
    cfg = read_config()

    # 1. User-defined
    user_path = cfg.get("db_path")
    if user_path:
        p = Path(user_path)
        if p.exists():
            return p

    # 2. Default server
    if DEFAULT_SERVER_PATH.exists():
        return DEFAULT_SERVER_PATH

    # 3. Local fallback
    LOCAL_BASE.mkdir(parents=True, exist_ok=True)
    return LOCAL_BASE


def set_db_path(new_path: str) -> None:
    """Save a user-defined database directory to config.json."""
    write_config({"db_path": str(new_path)})


def get_current_db_path_label() -> str:
    """Human-readable path for display in UI."""
    return str(get_db_base_path())


# ─── Resolved paths ───────────────────────────────────────────────────────────
BASE_PATH        = get_db_base_path()
DATABASE_PATH    = BASE_PATH / "fat_system.db"
ATTACHMENTS_PATH = BASE_PATH / "attachments"
BACKUPS_PATH     = BASE_PATH / "backups"

ATTACHMENT_FOLDERS = ["reports", "references", "emails", "photos", "drawings"]

# ─── Assets ───────────────────────────────────────────────────────────────────
if getattr(sys, 'frozen', False):
    ASSETS_PATH = Path(sys._MEIPASS) / "assets"
else:
    ASSETS_PATH = Path(__file__).parent.parent / "assets"

LOGO_PATH = ASSETS_PATH / "logo.png"

# ─── AI (Google Gemini) ───────────────────────────────────────────────────────
import os
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL   = "gemini-1.5-flash"

# ─── FAT Statuses ─────────────────────────────────────────────────────────────
FAT_STATUSES = [
    "Pending",
    "Approved",
    "Rejected",
    "Approved with comments",
]

STATUS_COLORS = {
    "Approved":               "#2ECC71",
    "Rejected":               "#E74C3C",
    "Pending":                "#F39C12",
    "Approved with comments": "#F1C40F",
}

INSPECTION_TYPES = ["FAT", "Visual Inspection", "Both"]

ALLOWED_EXTENSIONS = {
    "pdf":  "PDF Files (*.pdf)",
    "docx": "Word Files (*.docx)",
    "xlsx": "Excel Files (*.xlsx)",
    "msg":  "Email Files (*.msg)",
    "jpg":  "JPEG Images (*.jpg *.jpeg)",
    "png":  "PNG Images (*.png)",
    "zip":  "ZIP Archives (*.zip)",
}

ROLES = ["Admin", "Engineer"]

DEFAULT_ADMIN_USERNAME = "admin"
DEFAULT_ADMIN_PASSWORD = "admin123"

# ─── UI Theme ─────────────────────────────────────────────────────────────────
THEME = {
    "primary":      "#1A3A5C",
    "secondary":    "#2980B9",
    "accent":       "#E67E22",
    "bg":           "#F5F6FA",
    "surface":      "#FFFFFF",
    "text":         "#2C3E50",
    "text_light":   "#7F8C8D",
    "border":       "#DEE2E6",
    "sidebar_bg":   "#F5F6FA",
    "sidebar_text": "#2C3E50",
    "sidebar_hover":"#E8EEF4",
}
