"""ui/dashboard/dashboard_widget.py"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QSizePolicy, QGridLayout,
)
from PyQt6.QtCore    import Qt
from PyQt6.QtCharts  import QChart, QChartView, QBarSeries, QBarSet, QBarCategoryAxis, \
                            QValueAxis, QPieSeries
from PyQt6.QtGui     import QPainter, QColor

from config.settings       import THEME as T, COMPANY_NAME
from services.fat_service  import FATService

MONTH_NAMES = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]


class StatCard(QFrame):
    def __init__(self, label: str, value: str, color: str, parent=None):
        super().__init__(parent)
        self.setFixedHeight(110)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setStyleSheet(f"""
            QFrame {{
                background: white;
                border-radius: 10px;
                border-left: 5px solid {color};
                border-top: 1px solid #e0e0e0;
                border-right: 1px solid #e0e0e0;
                border-bottom: 1px solid #e0e0e0;
            }}
        """)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(18, 14, 18, 14)

        val_lbl = QLabel(value)
        val_lbl.setStyleSheet(f"font-size: 34px; font-weight: bold; color: {color}; border: none;")
        lay.addWidget(val_lbl)

        lbl = QLabel(label)
        lbl.setStyleSheet(f"font-size: 12px; color: {T['text_light']}; border: none;")
        lay.addWidget(lbl)


class DashboardWidget(QWidget):
    def __init__(self, session, current_user, parent=None):
        super().__init__(parent)
        self.session      = session
        self.current_user = current_user
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(20)

        # Page title
        title_row = QHBoxLayout()
        title = QLabel("Dashboard")
        title.setStyleSheet(f"font-size: 22px; font-weight: bold; color: {T['primary']};")
        title_row.addWidget(title)
        title_row.addStretch()
        welcome = QLabel(f"Welcome, {self.current_user.full_name or self.current_user.username}")
        welcome.setStyleSheet(f"color: {T['text_light']}; font-size: 13px;")
        title_row.addWidget(welcome)
        root.addLayout(title_row)

        # Stat cards row
        self.cards_row = QHBoxLayout()
        self.cards_row.setSpacing(16)
        root.addLayout(self.cards_row)

        # Charts row
        charts_row = QHBoxLayout()
        charts_row.setSpacing(16)

        self.bar_view = self._empty_chart_view("Monthly FAT Trend")
        self.pie_view = self._empty_chart_view("FAT by Status")
        charts_row.addWidget(self.bar_view, 3)
        charts_row.addWidget(self.pie_view, 2)
        root.addLayout(charts_row)

        # Supplier chart
        self.sup_view = self._empty_chart_view("FAT by Supplier")
        root.addWidget(self.sup_view)

    def _empty_chart_view(self, title: str) -> QChartView:
        chart = QChart()
        chart.setTitle(title)
        chart.setBackgroundRoundness(8)
        chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        view = QChartView(chart)
        view.setRenderHint(QPainter.RenderHint.Antialiasing)
        view.setMinimumHeight(240)
        view.setStyleSheet("border-radius: 8px; background: white;")
        return view

    # ── Refresh ───────────────────────────────────────────────────────────
    def refresh(self):
        svc    = FATService(self.session)
        counts = svc.get_status_counts()
        total  = sum(counts.values())

        # Clear old cards
        while self.cards_row.count():
            item = self.cards_row.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        status_cards = [
            ("Total Records",           str(total),                       T['primary']),
            ("Approved",                str(counts.get("Approved", 0)),   "#27ae60"),
            ("Rejected",                str(counts.get("Rejected", 0)),   "#e74c3c"),
            ("Pending",                 str(counts.get("Pending", 0)),    "#e67e22"),
            ("Approved with comments",  str(counts.get("Approved with comments", 0)), "#f39c12"),
        ]
        for label, value, color in status_cards:
            self.cards_row.addWidget(StatCard(label, value, color))

        self._build_bar_chart(svc.get_monthly_counts())
        self._build_pie_chart(counts)
        self._build_supplier_chart(svc.get_supplier_counts())

    def _build_bar_chart(self, data: list[dict]):
        chart = self.bar_view.chart()
        chart.removeAllSeries()
        for ax in chart.axes():
            chart.removeAxis(ax)

        if not data:
            return

        bar_set = QBarSet("FAT Records")
        bar_set.setColor(QColor(T['secondary']))
        categories = []
        for d in data[-12:]:   # last 12 months
            bar_set.append(d["count"])
            categories.append(MONTH_NAMES[d["month"] - 1])

        series = QBarSeries()
        series.append(bar_set)
        chart.addSeries(series)

        axis_x = QBarCategoryAxis()
        axis_x.append(categories)
        chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
        series.attachAxis(axis_x)

        axis_y = QValueAxis()
        axis_y.setLabelFormat("%d")
        chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
        series.attachAxis(axis_y)

    def _build_pie_chart(self, counts: dict):
        chart = self.pie_view.chart()
        chart.removeAllSeries()

        colors = {
            "Approved":               "#27ae60",
            "Rejected":               "#e74c3c",
            "Pending":                "#e67e22",
            "Approved with comments": "#f39c12",
        }
        series = QPieSeries()
        for status, count in counts.items():
            if count > 0:
                sl = series.append(f"{status} ({count})", count)
                sl.setColor(QColor(colors.get(status, "#95a5a6")))
                sl.setLabelVisible(True)

        chart.addSeries(series)
        chart.legend().setAlignment(Qt.AlignmentFlag.AlignRight)

    def _build_supplier_chart(self, data: list[dict]):
        chart = self.sup_view.chart()
        chart.removeAllSeries()
        for ax in chart.axes():
            chart.removeAxis(ax)

        if not data:
            return

        top = data[:10]
        bar_set = QBarSet("FAT Records")
        bar_set.setColor(QColor(T['primary']))
        categories = []
        for d in top:
            bar_set.append(d["count"])
            categories.append(d["name"][:20])

        series = QBarSeries()
        series.append(bar_set)
        chart.addSeries(series)

        axis_x = QBarCategoryAxis()
        axis_x.append(categories)
        chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
        series.attachAxis(axis_x)

        axis_y = QValueAxis()
        axis_y.setLabelFormat("%d")
        chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
        series.attachAxis(axis_y)
