import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QTextEdit, QHBoxLayout, QFrame, QSizePolicy,QPushButton
)
from PyQt5.QtChart import QChart, QChartView, QPieSeries
from PyQt5.QtGui import QPainter, QFont, QIcon, QColor,QRegion, QPainterPath,QPixmap
from PyQt5.QtCore import Qt, QMargins,QRectF
import pyRserve
import os

class HomeTab(QWidget):
    def __init__(self):
        super().__init__()

        # Set main background color for the entire HomeTab
        self.setStyleSheet("background-color: #1a1b2f;")  # Navy blue background

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

        # Portfolio Overview
        layout.addLayout(self.create_portfolio_layout())

        # News Feed
        news_label, news_feed = self.create_news_feed()
        layout.addWidget(news_label)
        layout.addWidget(news_feed)

        # Set the layout to the HomeTab widget
        self.setLayout(layout)

    def create_metrics_layout(self):
        """Create layout for Key Metrics cards."""
        metrics_layout = QHBoxLayout()
        metrics_layout.addWidget(self.create_metric_card("Market Cap", "$2.5 Trillion"))
        metrics_layout.addWidget(self.create_metric_card("24h Volume", "$130 Billion"))
        metrics_layout.addWidget(self.create_metric_card("Cryptos", "7,000+"))
        return metrics_layout

    def create_metric_card(self, title, value):
        """Helper method to create a unified metric card with the main background color."""
        card = QFrame()
        card.setStyleSheet("background-color: #1f2235; border-radius: 10px; border: 1px solid #00bfa6; padding: 10px;")  # Dark purple with teal border

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
        summary_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #ffdd00; text-shadow: 1px 1px 3px black;")  # Gold text

        # Create table and set headers
        summary_table = QTableWidget(3, 6)
        summary_table.setHorizontalHeaderLabels(["Coin", "Current Price", "24h Change", "Market Cap", "24h Volume", "Circulating Supply"])

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

            QTableWidget::corner {
                background-color: #1a1b2f;
                border: 1px solid #ffdd00;
            }
        """)

        # Populate table with data and icons
        data = [
            ["Bitcoin", "$50,000", "+5%", "$1 Trillion", "$40 Billion", "18.7 Million BTC"],
            ["Ethereum", "$4,000", "-2%", "$500 Billion", "$20 Billion", "118 Million ETH"],
            ["Binance Coin", "$400", "+1%", "$60 Billion", "$5 Billion", "160 Million BNB"]
        ]
        for row, coin_data in enumerate(data):
            for col, value in enumerate(coin_data):
                item = QTableWidgetItem(value)
                if col == 2:  # Change column
                    if "+" in value:
                        item.setForeground(QColor("#00ff00"))  # Lime green for positive change
                    elif "-" in value:
                        item.setForeground(QColor("#ff004d"))  # Red for negative change
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
        summary_table.horizontalHeader().setStretchLastSection(True)  # Make last column stretchable

        # Remove scrollbars
        summary_table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        summary_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        return summary_label, summary_table

    def create_portfolio_layout(self):
        """Create portfolio distribution layout."""
        portfolio_layout = QVBoxLayout()
        portfolio_label = QLabel("Portfolio Distribution")
        portfolio_label.setAlignment(Qt.AlignCenter)
        portfolio_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #ffdd00; text-shadow: 1px 1px 3px black;")  # Gold text

        pie_chart = QPieSeries()
        pie_chart.append("Bitcoin", 40)
        pie_chart.append("Ethereum", 30)
        pie_chart.append("Others", 30)

        chart = QChart()
        chart.addSeries(pie_chart)
        chart.setTitle("Portfolio Distribution")
        chart.setBackgroundBrush(QColor(26, 27, 47, 0))  # Transparent background
        chart.setMargins(QMargins(0, 0, 0, 0))

        # Customize chart to fit the content
        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignBottom)

        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        chart_view.setStyleSheet("background-color: #1a1b2f; border-radius: 10px; border: 1px solid #00bfa6;")

        # Set the width to expand and height to be fixed based on content
        chart_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        chart_view.setMinimumWidth(500)
        chart_view.setFixedHeight(300)
        chart_view.setContentsMargins(0, 0, 0, 0)

        portfolio_layout.addWidget(portfolio_label)
        portfolio_layout.addWidget(chart_view)

        return portfolio_layout

    def create_news_feed(self):
        """Create news feed section."""
        news_label = QLabel("Latest Cryptocurrency News")
        news_label.setAlignment(Qt.AlignCenter)
        news_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #ffdd00; text-shadow: 1px 1px 3px black;")  # Gold text

        news_feed = QTextEdit()
        news_feed.setReadOnly(True)
        news_feed.setPlainText(
            "• Bitcoin hits new high!\n"
            "• Ethereum 2.0 upgrade scheduled.\n"
            "• Major financial institution adopts blockchain technology.\n"
        )
        news_feed.setStyleSheet("background-color: #1f2235; color: white; padding: 10px; border-radius: 10px; border: 1px solid #00bfa6;")

        return news_label, news_feed
    


class BitcoinTab(QWidget):
    def __init__(self):
        super().__init__()

        # Set layout for the tab
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Bitcoin Price Charts"))

        # Generate and load the R chart
        chart_path = self.create_r_chart()
        if chart_path:
            chart_label = QLabel()
            chart_label.setPixmap(QPixmap(chart_path))
            layout.addWidget(chart_label)
        else:
            error_label = QLabel("Failed to generate chart.")
            layout.addWidget(error_label)

        self.setLayout(layout)

    def create_r_chart(self):
        """Generate a chart using R via PyRserve and return its file path."""
        directory = os.getcwd()
        chart_path = os.path.join(directory,"graphs","r_generated_chart.png").replace("\\", "/")

        # Connect to Rserve manually
        try:
            conn = pyRserve.connect(host='localhost', port=6315)  # Replace 6312 with your custom port number

            # Define the R script
            r_script = f"""
                library(ggplot2)
                dir.create(dirname("{chart_path}"), showWarnings = FALSE)
                data <- data.frame(
                time = 1:100,
                price = cumsum(rnorm(100, 0, 1)) + 50
                )
                p <- ggplot(data, aes(x = time, y = price)) +
                geom_line(color = "blue", linewidth = 1) + 
                labs(x = "Time", y = "Price") +
                theme_minimal()
                ggsave("{chart_path}",plot = p, width = 4, height = 2, dpi = 150)
                """
            
            # Execute the R script using Rserve
            conn.eval(r_script)
            
            # Check if the chart file was generated and exists
            if os.path.exists(chart_path):
                return chart_path
            else:
                print("Chart not found at:", chart_path)  # Debugging output
                return None

        except Exception as e:
            print(f"Error interacting with Rserve: {e}")
            return None
        
        finally:
            # Close the Rserve connection
            conn.close()

class EthereumTab(QWidget):
    def __init__(self):
        super().__init__()

        # Set background color for Ethereum Tab
        self.setStyleSheet("background-color: #3C3C3D;")  # Ethereum color

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Ethereum Tab"))
        # Add relevant content for Ethereum Tab here
        self.setLayout(layout)

class BinanceTab(QWidget):
    def __init__(self):
        super().__init__()

        # Set background color for Binance Coin Tab
        self.setStyleSheet("background-color: #F2B731;")  # Binance Coin color

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Binance Coin Tab"))
        # Add relevant content for Binance Coin Tab here
        self.setLayout(layout)

class CryptoApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # Remove the default window frame
        self.setWindowFlags(Qt.FramelessWindowHint)

        self.setWindowTitle("Crypto Analysis")
        self.setGeometry(100, 100, 800, 600)

        # Rounded background
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1a1b2f;
                border: 1px solid #00bfa6;
                border-radius: 20px;
            }
        """)

        # Central widget setup
        self.tabs = QTabWidget(self)
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border: none; background-color: #1a1b2f; }
            QTabBar::tab { background-color: #1a1b2f; color: #ffdd00; border: 1px solid #00bfa6; padding: 5px; border-radius: 5px; }
            QTabBar::tab:selected { background-color: #00bfa6; color: black; }
            QTabBar::tab:hover { background-color: #2d2f3e; }
        """)
        self.setCentralWidget(self.tabs)

        # Add the home tab
        self.home_tab = HomeTab()
        self.tabs.addTab(self.home_tab, "Home")
        self.tabs.addTab(BitcoinTab(), "Bitcoin")
        self.tabs.addTab(EthereumTab(), "Ethereum")
        self.tabs.addTab(BinanceTab(), "Binance Coin")

        # Initialize variables for dragging
        self._drag_pos = None

        # Create custom window control buttons (Close, Minimize, Maximize)
        self.create_window_controls()

    def create_window_controls(self):
        """Create custom buttons for close, minimize, and maximize."""
        close_button = QPushButton("")
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #ff6f61;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 10px;
                padding: 5px;
                width: 20px;
                height: 5px;
            }
            QPushButton:hover {
                background-color: #ff3e2f;
            }
        """)
        close_button.clicked.connect(self.close)  # Close button action

        minimize_button = QPushButton("")
        minimize_button.setStyleSheet("""
            QPushButton {
                background-color: #ffbb33;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 10px;
                padding: 5px;
                width: 20px;
                height: 5px;
            }
            QPushButton:hover {
                background-color: #ff9900;
            }
        """)
        minimize_button.clicked.connect(self.showMinimized)  # Minimize button action

        maximize_button = QPushButton("")
        maximize_button.setStyleSheet("""
            QPushButton {
                background-color: #33cc33;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 10px;
                padding: 5px;
                width: 20px;
                height: 5px;
            }
            QPushButton:hover {
                background-color: #28a745;
            }
        """)
        maximize_button.clicked.connect(self.toggle_maximize)  # Maximize button action

        # Layout to position buttons horizontally
        controls_layout = QHBoxLayout()
        controls_layout.addWidget(minimize_button)
        controls_layout.addWidget(maximize_button)
        controls_layout.addWidget(close_button)

        # Create a container widget for the buttons and position it
        controls_widget = QWidget(self)
        controls_widget.setLayout(controls_layout)
        controls_widget.setGeometry(self.width() - 150, 5, 140, 50)  # Position in the top-right corner
        controls_widget.setStyleSheet("background: transparent;")  # Make sure the background is transparent for the buttons to show

    def toggle_maximize(self):
        """Toggle between maximize and restore."""
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def mousePressEvent(self, event):
        """Store the mouse position when the press event occurs."""
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPos()  # Store the initial mouse position
            event.accept()

    def mouseMoveEvent(self, event):
        """Move the window based on mouse movement."""
        if self._drag_pos:
            delta = event.globalPos() - self._drag_pos  # Calculate the movement
            self.move(self.pos() + delta)  # Move the window
            self._drag_pos = event.globalPos()  # Update the initial position for the next move
            event.accept()

    def mouseReleaseEvent(self, event):
        """Reset the drag position when the mouse button is released."""
        self._drag_pos = None

    def resizeEvent(self, event):
        """Override resize event to maintain rounded corners on all sides."""
        path = QPainterPath()
        # Convert QRect to QRectF to ensure compatibility with addRoundedRect
        rectF = QRectF(self.rect())  # Convert to QRectF (floating-point rectangle)
        path.addRoundedRect(rectF, 20, 20)  # Apply rounded corners with 20px radius
        mask = QRegion(path.toFillPolygon().toPolygon())  # Create mask from path
        self.setMask(mask)  # Apply the mask to the window
        super().resizeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CryptoApp()
    window.show()
    sys.exit(app.exec_())
