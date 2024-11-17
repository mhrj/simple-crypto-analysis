import os
from PyQt5.QtWidgets import (
   QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QTextEdit, QHBoxLayout, QFrame
)
from PyQt5.QtGui import QFont,QPixmap
from PyQt5.QtCore import Qt
from widget_classes.helper import Helper

class BinanceTab(QWidget):
    def __init__(self,conn):
        super().__init__()
        self.conn = conn

        # Main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(20)

        # Key Metrics Cards with unified look
        layout.addLayout(self.create_summary_widget())


        # Chart Area: Main Price Chart
        chart_label = self.add_price_chart()
        layout.addWidget(chart_label)

        # Bottom Section: Analysis
        layout.addLayout(self.create_bottom_section())

        self.setLayout(layout)
        
    def create_summary_widget(self):
        """Create layout for Key Metrics cards."""
        metrics_layout = QHBoxLayout()
        metrics_layout.addWidget(self.create_metric_card("Current Price", "$2.5 Trillion"))
        metrics_layout.addWidget(self.create_metric_card("Highest/Lowest price", "$130 Billion"))
        metrics_layout.addWidget(self.create_metric_card("Average Price Over Time", "7,000+"))
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
    
    def update_summary(self, current_price, avg_price, highest_price, lowest_price):
        """Update the price summary with new values."""
        self.current_price_label.setText(f"Current Price: ${current_price:.2f}")
        self.average_price_label.setText(f"Average Price: ${avg_price:.2f}")
        self.highest_price_label.setText(f"Highest Price: ${highest_price:.2f}")
        self.lowest_price_label.setText(f"Lowest Price: ${lowest_price:.2f}")

    def add_price_chart(self):
        """Generate and display the R-generated price chart inside a bordered frame."""
        chart_path = self.create_r_chart()
        chart_label = QLabel()

        if chart_path:
            chart_label.setPixmap(QPixmap(chart_path))
            chart_label.setAlignment(Qt.AlignCenter)
        else:
            chart_label.setText("Failed to generate chart.")
            chart_label.setStyleSheet("color: red; font-size: 16px;")
            chart_label.setAlignment(Qt.AlignCenter)

        # Create a frame to wrap the chart
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                border: 2px solid #00bfa6; /* Teal border */
                border-radius: 10px;      /* Optional: rounded corners */
                background-color: #1f2235; /* Dark background for the chart frame */
                margin-top: 20px;        /* Add space at the top */
            }
        """)

        # Add chart_label to the frame's layout
        frame_layout = QVBoxLayout()
        frame_layout.setContentsMargins(10, 10, 10, 10)  # Add internal padding
        frame_layout.addWidget(chart_label)
        frame.setLayout(frame_layout)

        return frame


    def create_r_chart(self):
        """Generate a chart using R via PyRserve and return its file path."""
        chart_path = Helper.create_chart_path("binance_price_chart.png")
        try:
            conn = self.conn

            r_script = f"""
                library(ggplot2)
                library(dplyr)
                dir.create(dirname("{chart_path}"), showWarnings = FALSE)

                data <- data.frame(
                    time = 1:100,
                    price = cumsum(rnorm(100, 0, 1)) + 50
                )

                data <- data %>%
                    mutate(
                        SMA_10 = zoo::rollmean(price, 10, fill = NA),
                        SMA_20 = zoo::rollmean(price, 20, fill = NA)
                    )

                p <- ggplot(data, aes(x = time)) +
                    geom_line(aes(y = price, color = "Price"), linewidth = 0.3) +
                    geom_line(aes(y = SMA_10, color = "10-Day SMA"), linetype = "dashed", linewidth = 0.3) +
                    geom_line(aes(y = SMA_20, color = "20-Day SMA"), linetype = "dotted", linewidth = 0.3) +
                    geom_point(data = data.frame(time = c(20, 50, 80), price = c(52, 48, 54)),
                            aes(x = time, y = price), color = "red", size = 3) +
                    labs(x = "Time", y = "Price") +
                    scale_color_manual(values = c("Price" = "blue", "10-Day SMA" = "green", "20-Day SMA" = "purple")) +
                    theme_minimal(base_family = "Arial") +
                    theme(
                        axis.text.x = element_text(color = "white", size = 10),
                        axis.text.y = element_text(color = "white", size = 10),
                        axis.title.x = element_text(color = "white", size = 12, face = "bold"),
                        axis.title.y = element_text(color = "white", size = 12, face = "bold"),
                        plot.title = element_text(color = "white", size = 14, face = "bold", hjust = 0.5),
                        legend.text = element_text(color = "white", size = 10),
                        legend.title = element_text(color = "white", size = 12),
                        panel.grid.major = element_line(color = "gray40"),
                        panel.grid.minor = element_line(color = "gray25")
                    )

                ggsave("{chart_path}", plot = p, width = 8, height = 6, dpi = 100)
                """

            conn.eval(r_script)
            if os.path.exists(chart_path):
                return chart_path
            else:
                return None

        except Exception as e:
            print(f"Error interacting with Rserve: {e}")
            return None

    def create_bottom_section(self):
        """Create layout for daily returns, sentiment analysis, and correlation matrix."""
        bottom_layout = QHBoxLayout()

        # Daily Returns Table
        daily_returns = self.create_daily_returns_table()
        bottom_layout.addWidget(daily_returns)

        # Sentiment Analysis Summary
        sentiment_summary = self.create_sentiment_summary()
        bottom_layout.addWidget(sentiment_summary)

        # Correlation Matrix Table
        correlation_matrix = self.create_correlation_matrix()
        bottom_layout.addWidget(correlation_matrix)

        return bottom_layout

    def create_daily_returns_table(self):
        """Create a table for daily returns."""
        daily_returns = QTableWidget(3, 2)
        daily_returns.setHorizontalHeaderLabels(["Date", "Daily Return (%)"])
        daily_returns.setStyleSheet("background-color: #ffdd00; color: white;")

        data = [
            ["2024-11-08", "+2.5%"],
            ["2024-11-09", "-1.2%"],
            ["2024-11-10", "+0.8%"]
        ]
        for row, row_data in enumerate(data):
            for col, value in enumerate(row_data):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignCenter)
                daily_returns.setItem(row, col, item)

        # Resize rows to fit content
        daily_returns.resizeRowsToContents()

        # Calculate the total height of the table to fit the content
        total_height = daily_returns.horizontalHeader().height()
        for row in range(daily_returns.rowCount()):
            total_height += daily_returns.rowHeight(row)

        # Set the table's height to the calculated value
        daily_returns.setFixedHeight(total_height)

        # Resize columns to fit content and stretch last column
        daily_returns.resizeColumnsToContents()
        daily_returns.horizontalHeader().setStretchLastSection(True)  # Make last column stretchable

        # Remove scrollbars
        daily_returns.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        daily_returns.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        daily_returns.resizeColumnsToContents()
        
        daily_returns.setStyleSheet("""
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
        
        return daily_returns
    
    
    def create_sentiment_summary(self):
        """Create a dynamically resizing text box for sentiment analysis summary."""
        sentiment_summary = QTextEdit()
        sentiment_summary.setReadOnly(True)
        sentiment_summary.setPlainText(
            "• Positive sentiment: 65%\n"
            "• Negative sentiment: 20%\n"
            "• Neutral sentiment: 15%"
        )
        sentiment_summary.setStyleSheet("background-color: #1a1b2f; color: white; padding: 10px;border: 1px solid #ffdd00;")

        # Perform initial adjustment of size to fit content
        self.adjust_text_edit_size(sentiment_summary)

        # Connect content changes to a resizing function
        sentiment_summary.document().contentsChanged.connect(
            lambda: self.adjust_text_edit_size(sentiment_summary)
        )

        return sentiment_summary

    def adjust_text_edit_size(self, text_edit):
        """Adjust the size of a QTextEdit widget based on its content."""
        # Get the height of the document
        doc_height = text_edit.document().size().height()
        
        # Add some padding for aesthetic purposes
        total_height = int(doc_height + text_edit.contentsMargins().top() + text_edit.contentsMargins().bottom() + 80)

        # Set the fixed height of the widget based on content
        text_edit.setFixedHeight(total_height)



    def create_correlation_matrix(self):
        """Create a table for correlation matrix."""
        correlation_matrix = QTableWidget(3, 3)
        correlation_matrix.setHorizontalHeaderLabels(["BTC", "ETH", "BNB"])
        correlation_matrix.setVerticalHeaderLabels(["BTC", "ETH", "BNB"])
        correlation_matrix.setStyleSheet("background-color: #ffdd00; color: white;")

        data = [
            [1.00, 0.85, 0.75],
            [0.85, 1.00, 0.70],
            [0.75, 0.70, 1.00]
        ]
        for row in range(3):
            for col in range(3):
                item = QTableWidgetItem(f"{data[row][col]:.2f}")
                item.setTextAlignment(Qt.AlignCenter)
                correlation_matrix.setItem(row, col, item)

        correlation_matrix.resizeColumnsToContents()
        # Resize rows to fit content
        correlation_matrix.resizeRowsToContents()

        # Calculate the total height of the table to fit the content
        total_height = correlation_matrix.horizontalHeader().height()
        for row in range(correlation_matrix.rowCount()):
            total_height += correlation_matrix.rowHeight(row)

        # Set the table's height to the calculated value
        correlation_matrix.setFixedHeight(total_height)

        # Resize columns to fit content and stretch last column
        correlation_matrix.resizeColumnsToContents()
        correlation_matrix.horizontalHeader().setStretchLastSection(True)  # Make last column stretchable

        # Remove scrollbars
        correlation_matrix.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        correlation_matrix.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        correlation_matrix.resizeColumnsToContents()
        
        correlation_matrix.setStyleSheet("""
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
        return correlation_matrix