from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView
from PyQt5.QtCore import Qt

class PortfolioNotificationTab(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            QWidget {
                background-color: #1a1b2f;
                color: white;
            }
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #ffdd00;
            }
            QTableWidget {
                background-color: #2d2f3e;
                color: white;
                border: 1px solid #00bfa6;
                gridline-color: #00bfa6;
            }
            QTableWidget::item {
                padding: 5px;
                border: none;
            }
        """)

        layout = QVBoxLayout()
        header = QLabel("Portfolio Notifications")
        header.setAlignment(Qt.AlignCenter)

        # Table widget to display data
        self.table = QTableWidget()
        self.table.setColumnCount(3)  # Adjust column count as needed
        self.table.setHorizontalHeaderLabels(["Name", "Joined At", "Data Sent"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #1a1b2f;
                color: white;
                border: 1px solid #ffdd00;
                outline: none;
            }

            QTableWidget::item {
                color: white;
                border: 1px solid #ffdd00;
            }

            QHeaderView::section {
                background-color: #1f2235;
                color: #00bfa6;
                font-weight: bold;
                border: 1px solid #ffdd00;
                padding: 10px;
                border-bottom: 1px solid #ffdd00;
                outline: none;
            }
            
            QTableCornerButton::section {
                background-color: #1a1b2f;
                border: 1px solid #ffdd00;  
            }

            QTableWidget::corner {
                background-color: #1a1b2f;
                border: 1px solid #ffdd00;
            }
        """)

        # Add widgets to layout
        layout.addWidget(header)
        layout.addWidget(self.table)
        self.setLayout(layout)

    def update_data(self, data):
        """
        Update table data dynamically.
        :param data: List of dictionaries with keys 'name', 'joined_at', 'data_sent'
        """
        self.table.setRowCount(len(data))
        for row, entry in enumerate(data):
            self.table.setItem(row, 0, QTableWidgetItem(entry.get("name", "Unknown")))
            self.table.setItem(row, 1, QTableWidgetItem(entry.get("joined_at", "Unknown")))
            self.table.setItem(row, 2, QTableWidgetItem(entry.get("data_sent", "Unknown")))
