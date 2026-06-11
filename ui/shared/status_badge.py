"""ui/shared/status_badge.py"""
from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore    import Qt
from config.settings import STATUS_COLORS


class StatusBadge(QLabel):
    def __init__(self, status: str, parent=None):
        super().__init__(status, parent)
        self.setStatus(status)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFixedWidth(160)

    def setStatus(self, status: str):
        self.setText(status)
        color = STATUS_COLORS.get(status, "#95a5a6")
        text_color = "#333" if status == "Approved with comments" else "white"
        self.setStyleSheet(
            f"background-color: {color}; color: {text_color};"
            f"border-radius: 4px; padding: 3px 8px;"
            f"font-size: 11px; font-weight: bold;"
        )
