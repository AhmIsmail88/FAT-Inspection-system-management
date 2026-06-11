"""ui/projects/project_widget.py"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit,
    QDialog, QFormLayout, QTextEdit, QComboBox, QMessageBox, QFrame,
    QAbstractItemView,
)
from PyQt6.QtCore import Qt
from config.settings import THEME as T
from models.project  import Project


class ProjectWidget(QWidget):
    def __init__(self, session, current_user, parent=None):
        super().__init__(parent)
        self.session      = session
        self.current_user = current_user
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 18, 20, 18)
        root.setSpacing(14)

        hdr = QHBoxLayout()
        title = QLabel("Projects")
        title.setStyleSheet(f"font-size:22px;font-weight:bold;color:{T['primary']};")
        hdr.addWidget(title)
        hdr.addStretch()

        add_btn = QPushButton("＋  Add Project")
        add_btn.setStyleSheet(f"background-color:{T['primary']}; color:white; font-weight:bold; padding:0 16px; border-radius:4px;")
        add_btn.setFixedHeight(34)
        add_btn.clicked.connect(self._add)
        
        self.edit_btn = QPushButton("✏️  Edit")
        self.edit_btn.setStyleSheet(f"background-color:{T['secondary']}; color:white; font-weight:bold; padding:0 16px; border-radius:4px;")
        self.edit_btn.setFixedHeight(34)
        self.edit_btn.clicked.connect(self._edit)
        self.edit_btn.setEnabled(False)
        
        self.del_btn = QPushButton("🗑  Delete")
        self.del_btn.setStyleSheet("background-color:#c0392b; color:white; font-weight:bold; padding:0 16px; border-radius:4px;")
        self.del_btn.setFixedHeight(34)
        self.del_btn.clicked.connect(self._delete)
        self.del_btn.setEnabled(False)
        
        hdr.addWidget(add_btn)
        hdr.addWidget(self.edit_btn)
        hdr.addWidget(self.del_btn)
        root.addLayout(hdr)

        self.search = QLineEdit()
        self.search.setPlaceholderText("🔍  Search projects…")
        self.search.setObjectName("search_bar")
        self.search.textChanged.connect(self.refresh)
        root.addWidget(self.search)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["#", "Project Name", "Client", "Status", "Notes"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.itemSelectionChanged.connect(self._on_selection_changed)
        self.table.doubleClicked.connect(self._edit)
        root.addWidget(self.table)

    def _on_selection_changed(self):
        has_sel = len(self.table.selectedItems()) > 0
        self.edit_btn.setEnabled(has_sel)
        self.del_btn.setEnabled(has_sel)

    def refresh(self):
        keyword = self.search.text().strip() if hasattr(self, 'search') else ""
        q = self.session.query(Project).order_by(Project.project_name)
        if keyword:
            q = q.filter(Project.project_name.ilike(f"%{keyword}%"))
        projects = q.all()

        self.table.setRowCount(len(projects))
        for i, p in enumerate(projects):
            self.table.setItem(i, 0, QTableWidgetItem(str(p.id)))
            self.table.setItem(i, 1, QTableWidgetItem(p.project_name or ""))
            self.table.setItem(i, 2, QTableWidgetItem(p.client_name or ""))
            self.table.setItem(i, 3, QTableWidgetItem(p.status or ""))
            self.table.setItem(i, 4, QTableWidgetItem(p.notes or ""))
            for c in range(5):
                if self.table.item(i, c):
                    self.table.item(i, c).setData(Qt.ItemDataRole.UserRole, p.id)

    def _add(self):
        dlg = ProjectDialog(self.session, parent=self)
        if dlg.exec():
            self.refresh()

    def _edit(self):
        row = self.table.currentRow()
        if row < 0: return
        pid = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        dlg = ProjectDialog(self.session, pid, parent=self)
        if dlg.exec(): self.refresh()

    def _delete(self):
        row = self.table.currentRow()
        if row < 0: return
        pid = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        name = self.table.item(row, 1).text()
        reply = QMessageBox.question(self, "Confirm Delete", f"Are you sure you want to delete project '{name}'?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            try:
                p = self.session.get(Project, pid)
                if p:
                    self.session.delete(p)
                    self.session.commit()
                    self.refresh()
            except Exception as e:
                self.session.rollback()
                QMessageBox.critical(self, "Error", f"Cannot delete project because it is in use.\n\nDetails: {str(e)}")


class ProjectDialog(QDialog):
    def __init__(self, session, project_id=None, parent=None):
        super().__init__(parent)
        self.session    = session
        self.project_id = project_id
        self.setWindowTitle("Edit Project" if project_id else "Add Project")
        self.setMinimumWidth(460)
        self._build_ui()
        if project_id:
            self._load()

    def _build_ui(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(20, 20, 20, 20)
        lay.setSpacing(12)

        form = QFormLayout()
        self.name_edit   = QLineEdit()
        self.code_edit   = QLineEdit()
        self.client_edit = QLineEdit()
        self.status_cb   = QComboBox()
        self.status_cb.addItems(["Active", "Completed", "Archived"])
        self.notes_edit  = QTextEdit()
        self.notes_edit.setMaximumHeight(80)

        form.addRow("Project Name *", self.name_edit)
        form.addRow("Project Code",   self.code_edit)
        form.addRow("Client Name",    self.client_edit)
        form.addRow("Status",         self.status_cb)
        form.addRow("Notes",          self.notes_edit)
        lay.addLayout(form)

        btns = QHBoxLayout()
        btns.addStretch()
        cancel = QPushButton("Cancel"); cancel.clicked.connect(self.reject)
        save   = QPushButton("Save");   save.clicked.connect(self._save)
        save.setStyleSheet(f"background:{T['primary']};color:white;border-radius:5px;padding:6px 20px;")
        btns.addWidget(cancel); btns.addWidget(save)
        lay.addLayout(btns)

    def _load(self):
        p = self.session.get(Project, self.project_id)
        if not p: return
        self.name_edit.setText(p.project_name or "")
        self.code_edit.setText(p.project_code or "")
        self.client_edit.setText(p.client_name or "")
        self.status_cb.setCurrentText(p.status or "Active")
        self.notes_edit.setPlainText(p.notes or "")

    def _save(self):
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Validation", "Project name is required.")
            return
        if self.project_id:
            p = self.session.get(Project, self.project_id)
        else:
            p = Project()
            self.session.add(p)
        p.project_name = name
        p.project_code = self.code_edit.text().strip() or None
        p.client_name  = self.client_edit.text().strip() or None
        p.status       = self.status_cb.currentText()
        p.notes        = self.notes_edit.toPlainText().strip() or None
        self.session.commit()
        self.accept()
