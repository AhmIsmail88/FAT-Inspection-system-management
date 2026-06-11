"""
ui/settings/audit_details_dialog.py
───────────────────────────────────
Dialog to show the details of an audit log entry (Old vs New value).
"""
import json
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QPushButton, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from config.settings import THEME as T


class AuditDetailsDialog(QDialog):
    def __init__(self, action: str, old_value: str, new_value: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Audit Log Details - {action}")
        self.setMinimumWidth(700)
        self.setMinimumHeight(500)
        
        self.action = action
        self.old_val = old_value
        self.new_val = new_value
        
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Header
        header = QFrame()
        header.setFixedHeight(50)
        header.setStyleSheet(f"background-color: {T['primary']};")
        h_lay = QHBoxLayout(header)
        h_lay.setContentsMargins(16, 0, 16, 0)
        
        title = QLabel(f"🔍 Audit Details: {self.action}")
        title.setStyleSheet("color: white; font-size: 15px; font-weight: bold;")
        h_lay.addWidget(title)
        
        root.addWidget(header)

        # Body
        body = QFrame()
        body.setStyleSheet("background-color: white;")
        b_lay = QVBoxLayout(body)
        b_lay.setContentsMargins(20, 20, 20, 20)
        
        # Split layout for Old vs New
        split_lay = QHBoxLayout()
        split_lay.setSpacing(20)
        
        # Old Value
        old_group = QVBoxLayout()
        old_lbl = QLabel("Old Value (Before):")
        old_lbl.setStyleSheet(f"color: {T['text_light']}; font-weight: bold;")
        old_group.addWidget(old_lbl)
        
        self.old_text = QTextEdit()
        self.old_text.setReadOnly(True)
        self.old_text.setStyleSheet(f"border: 1px solid {T['border']}; border-radius: 5px; background-color: #fdf2f2;")
        self._format_json(self.old_text, self.old_val)
        old_group.addWidget(self.old_text)
        
        split_lay.addLayout(old_group)
        
        # New Value
        new_group = QVBoxLayout()
        new_lbl = QLabel("New Value (After):")
        new_lbl.setStyleSheet(f"color: {T['text_light']}; font-weight: bold;")
        new_group.addWidget(new_lbl)
        
        self.new_text = QTextEdit()
        self.new_text.setReadOnly(True)
        self.new_text.setStyleSheet(f"border: 1px solid {T['border']}; border-radius: 5px; background-color: #f2fdf5;")
        self._format_json(self.new_text, self.new_val)
        new_group.addWidget(self.new_text)
        
        split_lay.addLayout(new_group)
        
        b_lay.addLayout(split_lay)
        root.addWidget(body)
        
        # Footer
        footer = QFrame()
        footer.setStyleSheet(f"background-color: {T['bg']}; border-top: 1px solid {T['border']};")
        f_lay = QHBoxLayout(footer)
        f_lay.setContentsMargins(20, 10, 20, 10)
        f_lay.addStretch()
        
        close_btn = QPushButton("Close")
        close_btn.setFixedHeight(36)
        close_btn.setStyleSheet(
            f"background-color: {T['primary']}; color: white; border-radius: 5px; padding: 0 20px; font-weight: bold;"
        )
        close_btn.clicked.connect(self.accept)
        f_lay.addWidget(close_btn)
        
        root.addWidget(footer)

    def _format_json(self, widget: QTextEdit, json_str: str):
        if not json_str:
            widget.setText("None")
            return
            
        try:
            data = json.loads(json_str)
            formatted = json.dumps(data, indent=4, ensure_ascii=False)
            widget.setText(formatted)
        except Exception:
            widget.setText(json_str)

        # Use monospaced font for JSON
        font = QFont("Consolas")
        font.setPointSize(11)
        widget.setFont(font)
