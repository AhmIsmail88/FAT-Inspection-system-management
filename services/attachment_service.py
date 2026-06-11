"""services/attachment_service.py"""
import shutil
import os
import subprocess
import sys
from pathlib import Path
from sqlalchemy.orm import Session

from models.attachment import Attachment
from config.settings   import ATTACHMENTS_PATH

# Map extension → folder category
EXT_CATEGORY = {
    "pdf":  "reports",
    "docx": "reports",
    "xlsx": "reports",
    "msg":  "emails",
    "eml":  "emails",
    "jpg":  "photos",
    "jpeg": "photos",
    "png":  "photos",
    "zip":  "references",
    "rar":  "references",
    "dwg":  "drawings",
    "dxf":  "drawings",
}

FILE_ICONS = {
    "pdf":  "📄",
    "docx": "📝",
    "xlsx": "📊",
    "msg":  "📧",
    "eml":  "📧",
    "jpg":  "🖼️",
    "jpeg": "🖼️",
    "png":  "🖼️",
    "zip":  "🗜️",
    "rar":  "🗜️",
    "dwg":  "📐",
    "dxf":  "📐",
}


class AttachmentService:
    def __init__(self, session: Session, current_user_id: int | None = None):
        self.session         = session
        self.current_user_id = current_user_id

    # ── Upload ────────────────────────────────────────────────────────────
    def upload(self, fat_record_id: int, source_path: str,
               category: str | None = None) -> Attachment:
        """Copy a file into the managed folder and register in DB."""
        src = Path(source_path)
        ext = src.suffix.lstrip(".").lower()

        # Auto-detect category if not provided
        if not category:
            category = EXT_CATEGORY.get(ext, "references")

        dest_dir = ATTACHMENTS_PATH / category
        dest_dir.mkdir(parents=True, exist_ok=True)

        # Avoid name collision
        dest    = dest_dir / src.name
        counter = 1
        while dest.exists():
            dest = dest_dir / f"{src.stem}_{counter}{src.suffix}"
            counter += 1

        shutil.copy2(src, dest)

        attachment = Attachment(
            fat_record_id = fat_record_id,
            file_name     = src.name,
            file_type     = ext,
            file_path     = str(dest.relative_to(ATTACHMENTS_PATH)),
            uploaded_by   = self.current_user_id,
        )
        self.session.add(attachment)
        self.session.commit()
        return attachment

    def upload_multiple(self, fat_record_id: int,
                        paths: list[str]) -> list[Attachment]:
        results = []
        for p in paths:
            try:
                results.append(self.upload(fat_record_id, p))
            except Exception:
                pass
        return results

    # ── Replace ───────────────────────────────────────────────────────────
    def replace(self, attachment_id: int, new_source_path: str) -> Attachment:
        """Replace the file on disk but keep the DB record."""
        att      = self.session.get(Attachment, attachment_id)
        if not att:
            raise FileNotFoundError(f"Attachment #{attachment_id} not found")

        old_path = ATTACHMENTS_PATH / att.file_path
        new_src  = Path(new_source_path)

        if old_path.exists():
            old_path.unlink()

        shutil.copy2(new_src, old_path.parent / new_src.name)
        new_dest = old_path.parent / new_src.name

        att.file_name = new_src.name
        att.file_type = new_src.suffix.lstrip(".").lower()
        att.file_path = str(new_dest.relative_to(ATTACHMENTS_PATH))
        self.session.commit()
        return att

    # ── Delete ────────────────────────────────────────────────────────────
    def delete(self, attachment_id: int) -> None:
        att = self.session.get(Attachment, attachment_id)
        if not att:
            raise FileNotFoundError(f"Attachment #{attachment_id} not found")
        full_path = ATTACHMENTS_PATH / att.file_path
        if full_path.exists():
            full_path.unlink()
        self.session.delete(att)
        self.session.commit()

    # ── Open ──────────────────────────────────────────────────────────────
    def open_file(self, attachment_id: int) -> None:
        """Open with default OS application (Windows/Linux/Mac)."""
        att = self.session.get(Attachment, attachment_id)
        if not att:
            raise FileNotFoundError(f"Attachment #{attachment_id} not found")
        full_path = ATTACHMENTS_PATH / att.file_path
        if not full_path.exists():
            raise FileNotFoundError(f"File not on disk: {full_path}")

        if sys.platform == "win32":
            os.startfile(str(full_path))
        elif sys.platform == "darwin":
            subprocess.run(["open", str(full_path)])
        else:
            subprocess.run(["xdg-open", str(full_path)])

    def open_folder(self, attachment_id: int) -> None:
        """Open the containing folder in Explorer."""
        att = self.session.get(Attachment, attachment_id)
        if not att:
            return
        folder = (ATTACHMENTS_PATH / att.file_path).parent
        if sys.platform == "win32":
            subprocess.run(["explorer", str(folder)])
        else:
            subprocess.run(["xdg-open", str(folder)])

    # ── Query ─────────────────────────────────────────────────────────────
    def get_for_record(self, fat_record_id: int) -> list[Attachment]:
        return (
            self.session.query(Attachment)
            .filter_by(fat_record_id=fat_record_id)
            .order_by(Attachment.uploaded_at.desc())
            .all()
        )

    def get_full_path(self, attachment_id: int) -> Path:
        att = self.session.get(Attachment, attachment_id)
        if not att:
            raise FileNotFoundError
        return ATTACHMENTS_PATH / att.file_path

    # ── Helpers ───────────────────────────────────────────────────────────
    @staticmethod
    def file_size_str(path: Path) -> str:
        if not path.exists():
            return "missing"
        size = path.stat().st_size
        if size < 1024:
            return f"{size} B"
        if size < 1024 ** 2:
            return f"{size/1024:.1f} KB"
        return f"{size/1024**2:.1f} MB"

    @staticmethod
    def icon_for(file_type: str) -> str:
        return FILE_ICONS.get((file_type or "").lower(), "📎")
