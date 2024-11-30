import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QHBoxLayout, QPushButton, QSplashScreen,QLabel,QVBoxLayout
)
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve,QRectF,QPoint
from PyQt5.QtGui import QPixmap,QPainterPath,QRegion,QPolygon,QColor
import pyRserve
from widget_classes import home_tab, bitcoin_tab, ethereum_tab, binance_tab,online_R_interaction
import os

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
        
        # Create and set tabs
        self.home_tab = home_tab.HomeTab()
        self.tabs.addTab(self.home_tab, "Home")
        
        self.bitcoin_tab = bitcoin_tab.BitcoinTab()
        self.tabs.addTab(self.bitcoin_tab, "Bitcoin")
        
        self.ethereum_tab = ethereum_tab.EthereumTab()
        self.tabs.addTab(self.ethereum_tab, "Ethereum")
        
        self.binance_tab = binance_tab.BinanceTab()
        self.tabs.addTab(self.binance_tab, "Binance Coin")
        
        self.online_R_interaction_tab = online_R_interaction.OnlineRInteraction()
        self.tabs.addTab(self.online_R_interaction_tab, "R_Notifications")
        
        
        # Initialize variables for dragging
        self._drag_pos = None

        # Create custom window control buttons (Close, Minimize, Maximize)
        self.create_window_controls()

        # Show splash screen before the main window
        show_splash_screen_with_animation()

    def create_window_controls(self):
        """Create custom buttons for close, minimize, and maximize with dynamic positioning."""
        # Define buttons
        self.close_button = QPushButton("")
        self.close_button.setStyleSheet("""
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
        self.close_button.clicked.connect(self.close)

        self.minimize_button = QPushButton("-")
        self.minimize_button.setStyleSheet("""
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
        self.minimize_button.clicked.connect(self.showMinimized)

        self.maximize_button = QPushButton("")
        self.maximize_button.setStyleSheet("""
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
        self.maximize_button.clicked.connect(self.toggle_maximize)

        # Layout to position buttons horizontally
        self.controls_layout = QHBoxLayout()
        self.controls_layout.setContentsMargins(0, 0, 0, 0)
        self.controls_layout.addWidget(self.minimize_button)
        self.controls_layout.addWidget(self.maximize_button)
        self.controls_layout.addWidget(self.close_button)

        # Create a container widget for the buttons
        self.controls_widget = QWidget(self)
        self.controls_widget.setLayout(self.controls_layout)
        self.controls_widget.setStyleSheet("background: transparent;")  # Transparent background

        # Initial position
        self.update_window_controls_position()
        
        
    def update_window_controls_position(self):
        """Update the position of the window control buttons dynamically."""
        if self.isMaximized():
            # Center the controls at the top
            controls_width = self.controls_widget.sizeHint().width()
            self.controls_widget.setGeometry(
                (self.width() - controls_width) // 2,
                10,  # Top padding
                controls_width,
                self.controls_widget.sizeHint().height()
            )
        else:
            # Position at the top-right corner
            self.controls_widget.setGeometry(
                self.width() - self.controls_widget.sizeHint().width() - 10,  # Right padding
                10,  # Top padding
                self.controls_widget.sizeHint().width(),
                self.controls_widget.sizeHint().height()
            )


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
        self.update_window_controls_position()
        

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
