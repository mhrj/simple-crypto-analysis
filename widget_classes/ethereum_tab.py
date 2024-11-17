import os
from PyQt5.QtWidgets import (
   QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QTextEdit, QHBoxLayout, QFrame
)
from PyQt5.QtGui import QFont,QPixmap
from PyQt5.QtCore import Qt
from widget_classes.helper import Helper


class EthereumTab(QWidget):
    def __init__(self, conn):
        super().__init__()
        self.conn = conn
        self.init_ui()

    def init_ui(self):
        """Initialize the UI layout."""
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(20)

        layout.addLayout(self.create_summary_widget())  # Add key metrics
        layout.addWidget(self.add_price_chart())  # Add price chart
        layout.addLayout(self.create_bottom_section())  # Add bottom section

        self.setLayout(layout)

    def create_summary_widget(self):
        """Create and return the layout for Key Metrics cards."""
        metrics_layout = QHBoxLayout()
        metrics = [
            ("Current Price", "$2.5 Trillion"),
            ("Highest/Lowest price", "$130 Billion"),
            ("Average Price Over Time", "7,000+")
        ]
        for title, value in metrics:
            metrics_layout.addWidget(self.create_metric_card(title, value))
        return metrics_layout

    def create_metric_card(self, title, value):
        """Create a unified metric card with the main background color."""
        card = QFrame()
        card.setStyleSheet("background-color: #1f2235; border-radius: 10px; border: 1px solid #00bfa6; padding: 10px;")

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
        frame = self.create_frame_with_chart(chart_label)
        return frame

    def create_frame_with_chart(self, chart_label):
        """Create a frame with a chart label."""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                border: 2px solid #00bfa6;
                border-radius: 10px;
                background-color: #1f2235;
                margin-top: 20px;
            }
        """)

        frame_layout = QVBoxLayout()
        frame_layout.setContentsMargins(10, 10, 10, 10)
        frame_layout.addWidget(chart_label)
        frame.setLayout(frame_layout)

        return frame

    def create_r_chart(self):
        """Generate a chart using R via PyRserve and return its file path."""
        chart_path = Helper.create_chart_path("ethereum_price_chart.png")
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
            return chart_path if os.path.exists(chart_path) else None

        except Exception as e:
            print(f"Error interacting with Rserve: {e}")
            return None

    def create_bottom_section(self):
        """Create the bottom section with daily returns, sentiment analysis, and correlation matrix."""
        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(self.create_daily_returns_table())
        bottom_layout.addWidget(self.create_sentiment_summary())
        bottom_layout.addWidget(self.create_correlation_matrix())
        return bottom_layout

    def create_daily_returns_table(self):
        """Create and return a table for daily returns."""
        table = self.create_table_widget(3, 2, ["Date", "Daily Return (%)"], [
            ["2024-11-08", "+2.5%"],
            ["2024-11-09", "-1.2%"],
            ["2024-11-10", "+0.8%"]
        ])
        return table

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
        self.adjust_text_edit_size(sentiment_summary)
        sentiment_summary.document().contentsChanged.connect(
            lambda: self.adjust_text_edit_size(sentiment_summary)
        )
        return sentiment_summary

    def create_correlation_matrix(self):
        """Create and return a correlation matrix table."""
        correlation_matrix = self.create_table_widget(3, 3, ["BTC", "ETH", "BNB"], [
            [1.00, 0.85, 0.75],
            [0.85, 1.00, 0.70],
            [0.75, 0.70, 1.00]
        ])
        return correlation_matrix

    def create_table_widget(self, rows, cols, headers, data):
        """Create a table widget with specific data."""
        table = QTableWidget(rows, cols)
        table.setHorizontalHeaderLabels(headers)
        for row, row_data in enumerate(data):
            for col, value in enumerate(row_data):
                table.setItem(row, col, QTableWidgetItem(str(value)))
         # Resize rows to fit content
        table.resizeRowsToContents()

        # Calculate the total height of the table to fit the content
        total_height = table.horizontalHeader().height()
        for row in range(table.rowCount()):
            total_height += table.rowHeight(row)

        # Set the table's height to the calculated value
        table.setFixedHeight(total_height)

        # Resize columns to fit content and stretch last column
        table.resizeColumnsToContents()
        table.horizontalHeader().setStretchLastSection(True)  # Make last column stretchable

        # Remove scrollbars
        table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        table.resizeColumnsToContents()
        table.setStyleSheet("""
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
        table.horizontalHeader().setStyleSheet("color: #ffdd00; font-weight: bold;")
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        return table

    def adjust_text_edit_size(self, text_edit):
        """Adjust the size of a QTextEdit widget based on its content."""
        # Get the height of the document
        doc_height = text_edit.document().size().height()
        
        # Add some padding for aesthetic purposes
        total_height = int(doc_height + text_edit.contentsMargins().top() + text_edit.contentsMargins().bottom() + 80)

        # Set the fixed height of the widget based on content
        text_edit.setFixedHeight(total_height)

