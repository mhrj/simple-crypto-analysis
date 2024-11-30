import asyncio
import websockets
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView
from PyQt5.QtCore import Qt, QThread, pyqtSignal


class WebSocketClient(QThread):
    # Define a signal to pass received data to the main widget
    data_received = pyqtSignal(dict)

    def __init__(self, websocket_url):
        super().__init__()
        self.websocket_url = websocket_url
        self.running = True

    async def websocket_handler(self):
        async with websockets.connect(self.websocket_url) as websocket:
            while self.running:
                try:
                    # Receive data from the WebSocket
                    message = await websocket.recv()
                    self.data_received.emit(eval(message))  # Emit the data as a signal
                except Exception as e:
                    print(f"WebSocket error: {e}")
                    self.running = False

    def run(self):
        # Run the WebSocket handler
        asyncio.run(self.websocket_handler())

    def stop(self):
        self.running = False


class OnlineRInteraction(QWidget):
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
        self.table.setHorizontalHeaderLabels(["Name", "Command", "Output"])
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

        # Initialize WebSocket client
        self.websocket_url = "ws://127.0.0.1:8000/ws/notifications/"  # Replace with your WebSocket endpoint
        self.websocket_client = WebSocketClient(self.websocket_url)
        self.websocket_client.data_received.connect(self.handle_data)
        self.websocket_client.start()

    def update_data(self, data):
        """
        Update table data dynamically.
        :param data: List of dictionaries with keys 'name', 'command', 'output'
        """
        self.table.setRowCount(len(data))
        for row, entry in enumerate(data):
            self.table.setItem(row, 0, QTableWidgetItem(entry.get("name", "Unknown")))
            self.table.setItem(row, 1, QTableWidgetItem(entry.get("command", "Unknown")))
            self.table.setItem(row, 2, QTableWidgetItem(entry.get("output", "Unknown")))

    def handle_data(self, data):
        """
        Handle data received from the WebSocket.
        """
        self.update_data([data])  # Update the table with the new data

    def closeEvent(self, event):
        """
        Stop the WebSocket client when the widget is closed.
        """
        self.websocket_client.stop()
        self.websocket_client.wait()
        super().closeEvent(event)
