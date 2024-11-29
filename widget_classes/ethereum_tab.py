import os
import pandas as pd
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QTextEdit, QHBoxLayout, QFrame
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from PyQt5.QtWebEngineWidgets import QWebEngineView
from widget_classes.helper import Helper
import plotly.io as pio
import plotly.graph_objects as go


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
        layout.addWidget(self.add_charts())  # Add price chart
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

    def create_r_data_direct(self):
        """Generate data using R and return it as two Pandas DataFrames."""
        try:
            r_script = """
                library(dplyr)
                library(zoo)

                data <- data.frame(
                    time = 1:100,
                    price = cumsum(rnorm(100, 0, 1)) + 50
                )

                data <- data %>%
                    mutate(
                        SMA_10 = zoo::rollmean(price, 10, fill = NA),
                        SMA_20 = zoo::rollmean(price, 20, fill = NA)
                    )

                events <- data.frame(
                    time = c(20, 50, 80),
                    price = c(52, 48, 54)
                )

                list(data = data, events = events)
            """
            result = self.conn.eval(r_script)

            # Convert result to dictionaries manually
            data_dict_prices = {
                'time': result['data'][0],  # Time data
                'price': result['data'][1]  # Price data
            }

            data_dict_smas = {
                'time': result['data'][0],
                'price': result['data'][1],     # Use the same `time` index
                'SMA_10': result['data'][2],    # SMA 10 data
                'SMA_20': result['data'][3]     # SMA 20 data
            }

            # Create pandas DataFrames from dictionaries
            data_df = pd.DataFrame(data_dict_prices)  # Data for price chart
            events_df = pd.DataFrame(data_dict_smas)  # Data for SMA chart
            return data_df, events_df
        except Exception as e:
            print(f"Error interacting with Rserve: {e}")
            return None, None

    def add_charts(self):
        """Add the interactive Plotly charts."""
        data, events = self.create_r_data_direct()
        if data is None or events is None:
            chart_label = QLabel("Failed to generate chart.")
            chart_label.setStyleSheet("color: red; font-size: 16px;")
            chart_label.setAlignment(Qt.AlignCenter)
            return chart_label

        # Create the two charts
        price_fig = self.create_price_chart(data)  # Price chart from data_df
        sma_fig = self.create_sma_chart(events)    # SMA chart from events_df

        # Create PyQt widgets for the charts
        price_chart_widget = self.display_interactive_chart(price_fig)
        sma_chart_widget = self.display_interactive_chart(sma_fig)

        # Create a layout to hold both charts
        chart_layout = QVBoxLayout()
        chart_layout.addWidget(price_chart_widget)
        chart_layout.addWidget(sma_chart_widget)

        # Wrap in a frame
        frame = QFrame()
        frame.setLayout(chart_layout)
        frame.setStyleSheet("""
            QFrame {
                border: 2px solid #00bfa6;
                border-radius: 10px;
                background-color: #1f2235;
            }
        """)
        return frame

    def create_price_chart(self, data):
        """Create a Plotly chart for price."""
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=data['time'], y=data['price'], mode='lines', name='Price'))
        fig.update_layout(
            title="Price Chart",
            xaxis_title="Time",
            yaxis_title="Price",
            template="plotly_dark"
        )
        fig.update_layout(
            template="plotly_dark",  # Use the dark template
            paper_bgcolor="#1f2235",  # Outer graph area background
            plot_bgcolor="#1f2235"   # Plot area background
        )
        return fig

    def create_sma_chart(self, events):
        """Create a Plotly chart for SMA and events."""
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=events['time'], y=events['SMA_10'], mode='lines', name='10-Day SMA', line=dict(dash='dash',width=1)))
        fig.add_trace(go.Scatter(x=events['time'], y=events['SMA_20'], mode='lines', name='20-Day SMA', line=dict(dash='dot')))
        fig.add_trace(go.Scatter(x=events['time'], y=events['price'], mode='markers', name='Important Events', marker=dict(color='red', size=5)))
        fig.update_layout(
            title="SMA and Important Events",
            xaxis_title="Time",
            yaxis_title="Price",
            template="plotly_dark"
        )
        fig.update_layout(
            template="plotly_dark",  # Use the dark template
            paper_bgcolor="#1f2235",  # Outer graph area background
            plot_bgcolor="#1f2235"   # Plot area background
        )
        return fig

    def display_interactive_chart(self, fig):
        """Display an interactive Plotly chart."""
        # This function assumes you are using Plotly to embed the chart in a PyQt widget.
        # The implementation will depend on how you are embedding the chart.
        html_content = pio.to_html(fig, full_html=False,include_plotlyjs='cdn')
        webview = QWebEngineView()
        # Embed the HTML with dynamic resizing
        custom_html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Responsive Plotly Graph</title>
        <style>
            html, body {{
                margin: 0;
                padding: 0;
                background-color: #1f2235;
                color: white;
                width: 100%;
                height: 100%;
                overflow: hidden; /* Disable scrolling */
            }}
            #graph {{
                width: 100%;
                height: 100%;
            }}
        </style>
    </head>
    <body>
        <div id="graph">{html_content}</div>
        <script>
            // Adjust chart size dynamically
            window.addEventListener('resize', () => {{
                const graphs = document.querySelectorAll('.plotly-graph-div');
                graphs.forEach(graph => {{
                    Plotly.relayout(graph, {{
                        width: window.innerWidth,
                        height: window.innerHeight
                    }});
                }});
            }});
            // Trigger resize on load
            window.dispatchEvent(new Event('resize'));
        </script>
    </body>
    </html>
    """
        webview.setHtml(custom_html)
        webview.setAttribute(Qt.WA_TranslucentBackground, True)
        webview.setStyleSheet("background: transparent;")
        webview.page().setBackgroundColor(Qt.transparent)
        return webview


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

