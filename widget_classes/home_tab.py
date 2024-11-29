import sys
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QTextEdit, QHBoxLayout, QFrame, QSizePolicy
)
from PyQt5.QtChart import QChart, QChartView, QPieSeries, QPieSlice
from PyQt5.QtGui import QPainter, QFont, QColor, QBrush
from PyQt5.QtCore import Qt, QMargins
from widget_classes import OnboardingWidget


class HomeTab(QWidget):
    def __init__(self):
        super().__init__()

        # Set main background color for the entire HomeTab
        # Navy blue background
        self.setStyleSheet("background-color: #1a1b2f;")

        # Main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(20)

        # Key Metrics Cards with unified look
        layout.addLayout(self.create_metrics_layout())

        # Cryptocurrency Summary Table
        summary_label, summary_table = self.create_summary_table()
        layout.addWidget(summary_label)
        layout.addWidget(summary_table)

        self.onboarding_widget = OnboardingWidget.OnboardingWidget()
        board_title = QLabel("Cryptocurrency Risk Projections")
        board_title.setAlignment(Qt.AlignCenter)
        board_title.setFont(QFont("Arial", 18, QFont.Bold))
        board_title.setStyleSheet("color: #ffdd00;")  # Gold text
        layout.addWidget(board_title)
        layout.addWidget(self.onboarding_widget)

        # News Feed
        news_label, news_feed = self.create_news_feed()
        layout.addWidget(news_label)
        layout.addWidget(news_feed)

        # Set the layout to the HomeTab widget
        self.setLayout(layout)

    def create_metrics_layout(self):
        """Create layout for Key Metrics cards."""
        metrics_layout = QHBoxLayout()
        metrics_layout.addWidget(
            self.create_metric_card("Market Cap", "$2.5 Trillion"))
        metrics_layout.addWidget(
            self.create_metric_card("24h Volume", "$130 Billion"))
        metrics_layout.addWidget(self.create_metric_card("Cryptos", "7,000+"))
        return metrics_layout

    def create_metric_card(self, title, value):
        """Helper method to create a unified metric card with the main background color."""
        card = QFrame()
        # Dark purple with teal border
        card.setStyleSheet(
            "background-color: #1f2235; border-radius: 10px; border: 1px solid #00bfa6; padding: 10px;")

        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)

        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Arial", 10, QFont.Bold))
        title_label.setStyleSheet("color: #ffdd00;")  # Gold text

        value_label = QLabel(value)
        value_label.setAlignment(Qt.AlignCenter)
        value_label.setFont(QFont("Arial", 12))
        value_label.setStyleSheet("color: #00bfa6;")  # Teal text

        layout.addWidget(title_label)
        layout.addWidget(value_label)

        card.setLayout(layout)
        return card

    def create_summary_table(self):
        """Create the cryptocurrency summary table without scroll bars and with dynamic sizing."""
        summary_label = QLabel("Top Cryptocurrencies Summary")
        summary_label.setAlignment(Qt.AlignCenter)
        summary_label.setStyleSheet(
            "font-size: 18px; font-weight: bold; color: #ffdd00;")  # Gold text

        # Create table and set headers
        summary_table = QTableWidget(3, 6)
        summary_table.setHorizontalHeaderLabels(
            ["Coin", "Current Price", "24h Change", "Market Cap", "24h Volume", "Circulating Supply"])

        # Update background to navy blue and style headers
        summary_table.setStyleSheet("""
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

        # Populate table with data and icons
        data = [
            ["Bitcoin", "$50,000", "+5%", "$1 Trillion",
                "$40 Billion", "18.7 Million BTC"],
            ["Ethereum", "$4,000", "-2%", "$500 Billion",
                "$20 Billion", "118 Million ETH"],
            ["Binance Coin", "$400", "+1%", "$60 Billion",
                "$5 Billion", "160 Million BNB"]
        ]
        for row, coin_data in enumerate(data):
            for col, value in enumerate(coin_data):
                item = QTableWidgetItem(value)
                if col == 2:  # Change column
                    if "+" in value:
                        # Lime green for positive change
                        item.setForeground(QColor("#00ff00"))
                    elif "-" in value:
                        # Red for negative change
                        item.setForeground(QColor("#ff004d"))
                item.setFont(QFont("Arial", 10))
                summary_table.setItem(row, col, item)

        # Resize rows to fit content
        summary_table.resizeRowsToContents()

        # Calculate the total height of the table to fit the content
        total_height = summary_table.horizontalHeader().height()
        for row in range(summary_table.rowCount()):
            total_height += summary_table.rowHeight(row)

        # Set the table's height to the calculated value
        summary_table.setFixedHeight(total_height)

        # Resize columns to fit content and stretch last column
        summary_table.resizeColumnsToContents()
        summary_table.horizontalHeader().setStretchLastSection(
            True)  # Make last column stretchable

        # Remove scrollbars
        summary_table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        summary_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        return summary_label, summary_table

    def create_risk_layout(self):
        return

    def create_news_feed(self):
        """Create news feed section."""
        news_label = QLabel("Latest Cryptocurrency News")
        news_label.setAlignment(Qt.AlignCenter)
        news_label.setStyleSheet(
            "font-size: 18px; font-weight: bold; color: #ffdd00;")  # Gold text

        news_feed = QTextEdit()
        news_feed.setReadOnly(True)
        news_feed.setPlainText(
            "• Bitcoin hits new high!\n"
            "• Ethereum 2.0 upgrade scheduled.\n"
            "• Major financial institution adopts blockchain technology.\n"
        )
        news_feed.setStyleSheet(
            "background-color: #1f2235; color: white; padding: 10px; border-radius: 10px; border: 1px solid #00bfa6;")

        return news_label, news_feed
