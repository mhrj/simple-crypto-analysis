import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget,QHBoxLayout,QPushButton
)
import pyRserve
from PyQt5.QtGui import QRegion, QPainterPath
from PyQt5.QtCore import Qt,QRectF
from widget_classes import home_tab,bitcoin_tab,ethereum_tab,binance_tab

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
        self.home_tab = home_tab.HomeTab()
        self.tabs.addTab(self.home_tab, "Home")
        conn = pyRserve.connect(host='localhost', port=6312)
        self.tabs.addTab(bitcoin_tab.BitcoinTab(conn), "Bitcoin")
        self.tabs.addTab(ethereum_tab.EthereumTab(conn), "Ethereum")
        self.tabs.addTab(binance_tab.BinanceTab(conn), "Binance Coin")

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
        controls_widget.setGeometry(self.width() - 90, 0, 140, 50)  # Position in the top-right corner
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
