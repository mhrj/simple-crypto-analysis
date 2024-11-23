import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QHBoxLayout, QPushButton, QSplashScreen,QLabel,QVBoxLayout
)
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve,QRectF,QPoint
from PyQt5.QtGui import QPixmap,QPainterPath,QRegion,QPolygon,QColor
import pyRserve
from widget_classes import home_tab, bitcoin_tab, ethereum_tab, binance_tab,portfolio_notification_tab
import os

class CryptoApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        conn = pyRserve.connect(host='localhost', port=6312)

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
        
        # Create and set tabs
        self.home_tab = home_tab.HomeTab()
        self.tabs.addTab(self.home_tab, "Home")
        
        self.bitcoin_tab = bitcoin_tab.BitcoinTab(conn)
        self.tabs.addTab(self.bitcoin_tab, "Bitcoin")
        
        self.ethereum_tab = ethereum_tab.EthereumTab(conn)
        self.tabs.addTab(self.ethereum_tab, "Ethereum")
        
        self.binance_tab = binance_tab.BinanceTab(conn)
        self.tabs.addTab(self.binance_tab, "Binance Coin")
        
        self.portfolio_notifications_tab = portfolio_notification_tab.PortfolioNotificationTab()
        self.tabs.addTab(self.portfolio_notifications_tab, "Portfolio Notifications")
        
        
        # Initialize variables for dragging
        self._drag_pos = None

        # Create custom window control buttons (Close, Minimize, Maximize)
        self.create_window_controls()

        # Show splash screen before the main window
        show_splash_screen_with_animation()

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

        minimize_button = QPushButton("-")
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
        controls_widget.setGeometry(self.width() - 140, 0, 140, 50)  # Position in the top-right corner
        controls_widget.setStyleSheet("background: transparent;")  # Make sure the background is transparent for the buttons to show

    def fade_out_splash(self, splash):
        """Fade out the splash screen and close it."""
        fade_out_animation = QPropertyAnimation(splash, b"windowOpacity")
        fade_out_animation.setDuration(1000)  # Duration of the fade-out (in ms)
        fade_out_animation.setStartValue(1)  # Start opacity
        fade_out_animation.setEndValue(0)  # End opacity
        fade_out_animation.setEasingCurve(QEasingCurve.InOutQuad)  # Smooth fade
        fade_out_animation.finished.connect(splash.close)  # Close the splash screen after animation
        fade_out_animation.start()

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
    
        # Convert QPolygonF to QPolygon by converting QPointF to QPoint
        polygon = QPolygon([QPoint(int(point.x()), int(point.y())) for point in path.toFillPolygon()])
    
        # Create a QRegion using the converted QPolygon
        mask = QRegion(polygon)
        self.setMask(mask)  # Apply the mask to the window
        super().resizeEvent(event)
        

def show_splash_screen_with_animation():
    # Create splash screen
    splash_pix = QPixmap(400, 300)
    splash_pix.fill(QColor(30, 30, 30))
    splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)

    # Set up container and layout
    container = QWidget(splash)
    container.setGeometry(0, 0, 400, 300)
    layout = QVBoxLayout(container)

    # Top text label
    text_label = QLabel("Crypto Analysis \n kiau cs group", container)
    text_label.setStyleSheet("background-color: #1a1b2f;font-size: 25px; color: white; border-radius: 10px;border-top: 3px solid #008080;")
    text_label.setAlignment(Qt.AlignCenter)
    layout.addWidget(text_label)

    # Bottom image label
    image_label = QLabel(container)
    image_label.setStyleSheet("background-color: #1a1b2f; border-radius: 10px;border-bottom: 3px solid #008080;")
    image_label.setAlignment(Qt.AlignCenter)
    layout.addWidget(image_label)

    # Directory for images
    directory = os.getcwd()
    image_dir = os.path.join(directory, "splash_icons")
    if not os.path.exists(image_dir):
        print(f"Error: The directory '{image_dir}' does not exist!")
        return

    image_files = sorted(os.listdir(image_dir))
    if not image_files:
        print(f"Error: No image files found in '{image_dir}'!")
        return

    current_image_index = 0

    def update_image():
        nonlocal current_image_index
        
        image_path = os.path.join(image_dir, image_files[current_image_index])
        pixmap = QPixmap(image_path)

        if pixmap.isNull():
            print(f"Error: Failed to load image '{image_path}'!")
            return

        image_label.setPixmap(pixmap.scaled(200, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        current_image_index = (current_image_index + 1) % len(image_files)

    update_image()
    # Timer setup
    image_timer = QTimer()
    image_timer.timeout.connect(update_image)
    image_timer.start(1000)

    splash.show()

    QTimer.singleShot(3000, lambda: (image_timer.stop(), splash.close()))

    return splash


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Show splash screen
    splash = show_splash_screen_with_animation()

    # Create the main window after splash screen
    window = CryptoApp()

    # Wait for the splash screen to close before showing the main window
    QTimer.singleShot(3000, window.show)  # Delay main window appearance until splash fades out

    sys.exit(app.exec_())
