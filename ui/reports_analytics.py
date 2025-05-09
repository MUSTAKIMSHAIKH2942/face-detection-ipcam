from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QFileDialog
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from fpdf import FPDF
import csv


class ReportsAnalytics(QWidget):
    """Reports and analytics page."""
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """Initialise the reports layout."""
        main_layout = QVBoxLayout()

        # 1. Date Filters Layout
        filter_layout = QHBoxLayout()

        self.start_date_edit = QLineEdit()
        self.start_date_edit.setPlaceholderText("Start Date (YYYY-MM-DD)")
        self.end_date_edit = QLineEdit()
        self.end_date_edit.setPlaceholderText("End Date (YYYY-MM-DD)")

        self.apply_filter_btn = QPushButton("Apply Filter")
        self.apply_filter_btn.clicked.connect(self.apply_filters)

        filter_layout.addWidget(QLabel("From:"))
        filter_layout.addWidget(self.start_date_edit)
        filter_layout.addWidget(QLabel("To:"))
        filter_layout.addWidget(self.end_date_edit)
        filter_layout.addWidget(self.apply_filter_btn)

        main_layout.addLayout(filter_layout)

        # 2. Table for Reports
        self.reports_table = QTableWidget()
        self.reports_table.setColumnCount(5)
        self.reports_table.setHorizontalHeaderLabels(
            ["Timestamp", "Camera ID", "Plugin", "Detection Info", "Severity"]
        )
        self.reports_table.horizontalHeader().setStretchLastSection(True)
        self.reports_table.setSortingEnabled(True)

        main_layout.addWidget(self.reports_table)

        # 3. Export Buttons Layout
        export_layout = QHBoxLayout()

        self.export_csv_btn = QPushButton("Export to CSV")
        self.export_pdf_btn = QPushButton("Export to PDF")

        self.export_csv_btn.clicked.connect(self.export_to_csv)
        self.export_pdf_btn.clicked.connect(self.export_to_pdf)

        export_layout.addWidget(self.export_csv_btn)
        export_layout.addWidget(self.export_pdf_btn)

        main_layout.addLayout(export_layout)

        self.setLayout(main_layout)

    def apply_filters(self):
        """Dummy function for filter button."""
        print(f"[ReportsAnalytics] Filter applied from {self.start_date_edit.text()} to {self.end_date_edit.text()}")

    def add_report_entry(self, alert):
        """Add alert to report view."""
        row = self.reports_table.rowCount()
        self.reports_table.insertRow(row)

        cols = [
            alert.get("timestamp", ""),
            str(alert.get("camera_id", "")),
            alert.get("plugin_name", ""),
            alert.get("detection_info", ""),
            alert.get("severity", "")
        ]

        for i, val in enumerate(cols):
            cell = QTableWidgetItem(val)
            if i == 4:
                cell.setTextAlignment(Qt.AlignCenter)
                cell.setBackground(self.get_severity_color(val))
            self.reports_table.setItem(row, i, cell)

    def get_severity_color(self, level):
        level = level.lower()
        if level == "critical":
            return QColor(255, 102, 102)
        elif level == "high":
            return QColor(255, 153, 153)
        elif level == "medium":
            return QColor(255, 204, 153)
        return QColor(255, 255, 255)

    def export_to_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save CSV", "", "CSV Files (*.csv)")
        if path:
            with open(path, mode='w', newline='') as file:
                writer = csv.writer(file)
                headers = [self.reports_table.horizontalHeaderItem(i).text() for i in range(self.reports_table.columnCount())]
                writer.writerow(headers)
                for row in range(self.reports_table.rowCount()):
                    row_data = [self.reports_table.item(row, col).text() if self.reports_table.item(row, col) else '' for col in range(self.reports_table.columnCount())]
                    writer.writerow(row_data)
            print(f"[ReportsAnalytics] CSV exported to: {path}")

    def export_to_pdf(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save PDF", "", "PDF Files (*.pdf)")
        if path:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=10)
            headers = [self.reports_table.horizontalHeaderItem(i).text() for i in range(self.reports_table.columnCount())]
            pdf.cell(200, 10, txt="EyeQ Alert Reports", ln=True, align='C')
            pdf.ln(5)

            for header in headers:
                pdf.cell(40, 10, header, border=1)
            pdf.ln()

            for row in range(self.reports_table.rowCount()):
                for col in range(self.reports_table.columnCount()):
                    item = self.reports_table.item(row, col)
                    value = item.text() if item else ""
                    pdf.cell(40, 10, value, border=1)
                pdf.ln()

            pdf.output(path)
            print(f"[ReportsAnalytics] PDF exported to: {path}")
