import pandas as pd
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHBoxLayout, QFrame,QHeaderView
)
from PyQt5.QtGui import QFont,QPixmap
from PyQt5.QtCore import Qt,QTimer
from PyQt5.QtWebEngineWidgets import QWebEngineView
from widget_classes.helper import Helper
from backend.crypto_page.crypto_analysis import CryptoAnalysis
from backend.crypto_page.sentiment_analysis import SentimentAnalysis
import plotly.io as pio
import plotly.graph_objects as go
import json

class EthereumTab(QWidget):
    def __init__(self):
        super().__init__()
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

    def create_pie_chart_card(self):
        """Create a card with a pie chart."""
        card = QFrame()
        card.setStyleSheet("background-color: #1f2235; border-radius: 10px; border: 1px solid #00bfa6; padding: 10px;")

        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)

        # Add title
        title_label = QLabel("Sentiment Analysis")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Arial", 10, QFont.Bold))
        title_label.setStyleSheet("color: #ffdd00;")  # Gold text

        # Create the pie chart using Plotly
        chart_view = self.create_pie_chart()

        layout.addWidget(title_label)
        layout.addWidget(chart_view)

        card.setLayout(layout)
        return card

    def create_pie_chart(self):
        # get data from backend
        sentiment_analysis = SentimentAnalysis(1)
        sentiment_data = sentiment_analysis.calculate_sentiment_distribution(coin_name="ETH")
        """Generate a pie chart using Plotly and return it as a QWebEngineView."""
        # Example data
        labels = ['Positive', 'Negative', 'Neutral']
        values = [sentiment_data["positive"], sentiment_data["negative"], sentiment_data["neutral"]]
        colors = ['#00bfa6', '#ff6f61', '#ffbb33']

        # Create Plotly pie chart
        fig = go.Figure(data=[go.Pie(labels=labels, values=values, marker=dict(colors=colors))])
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="#1f2235",
            font=dict(color='white'),
            margin=dict(l=0, r=0, t=0, b=0)  # Remove margins
        )

        # Convert Plotly figure to HTML and render it in QWebEngineView
        chart_html = fig.to_html(include_plotlyjs='cdn')
        
        custom_html = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
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
                <div id="graph">{chart_html}</div>
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
        webview = QWebEngineView()
        webview.setAttribute(Qt.WA_TranslucentBackground, True)
        webview.setStyleSheet("background: transparent;")
        webview.page().setBackgroundColor(Qt.transparent)
        webview.setHtml(custom_html)

        return webview

    def create_summary_widget(self):
        # get price data from backend
        price_data = CryptoAnalysis.fetch_crypto_price_data("ETH")
        highest = price_data["highest"]
        lowest = price_data["lowest"]
        average = price_data["average"]
        """Create and return the layout for Key Metrics cards."""
        metrics_layout = QHBoxLayout()
        metrics = [
            ("Highest/Lowest price", f"${highest}/${lowest}"),
            ("Average Price Over Time", f"${average}")
        ]
        for title, value in metrics:
            metrics_layout.addWidget(self.create_metric_card(title, value))
        metrics_layout.addWidget(self.create_pie_chart_card())
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

    def create_r_data_direct(self):
        # get data from backend
        data_dict_prices = CryptoAnalysis.fetch_crypto_prices_over_time("ETH")
        data_dict_smas = CryptoAnalysis.calculate_indicators("ETH")

        # Create pandas DataFrames from dictionaries
        data_df = pd.DataFrame(data_dict_prices)  # Data for price chart
        events_df = pd.DataFrame(data_dict_smas)  # Data for SMA chart
        return data_df, events_df

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
        self.price_chart_widget = self.display_interactive_chart(price_fig)
        sma_chart_widget = self.display_interactive_chart(sma_fig)

        # Create a layout to hold both charts
        chart_layout = QVBoxLayout()
        chart_layout.addWidget(self.price_chart_widget)
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
        self.price_chart_fig = go.Figure()
        self.price_chart_fig.add_trace(go.Scatter(x=data['timestamps'], y=data['prices'], mode='lines', name='Price'))
        self.price_chart_fig.update_layout(
            title="Price Chart",
            xaxis_title="Time",
            yaxis_title="Price",
            template="plotly_dark"
        )
        self.price_chart_fig.update_layout(
            template="plotly_dark",  # Use the dark template
            paper_bgcolor="#1f2235",  # Outer graph area background
            plot_bgcolor="#1f2235"   # Plot area background
        )
        # Set up QTimer to fetch new data and update the chart
        self.price_chart_timer = QTimer()
        self.price_chart_timer.timeout.connect(self.update_price_chart_incremental)
        self.price_chart_timer.start(60000)  # Update every 1 minute
        return self.price_chart_fig
    
    def update_price_chart_incremental(self):
        """Fetch the latest price point and update the chart."""
        try:
            # Fetch the latest data point from the backend
            new_data = CryptoAnalysis.fetch_crypto_prices_over_time("ETH", 1)
            new_timestamp = new_data["timestamps"][0]
            new_price = new_data["prices"][0]
            # Update the existing trace
            self.price_chart_fig.data[0].x = list(self.price_chart_fig.data[0].x) + [new_timestamp]
            self.price_chart_fig.data[0].y = list(self.price_chart_fig.data[0].y) + [new_price]
            js_code = f"""
            var graphDiv = document.getElementById('graph');
            if (graphDiv) {{
                Plotly.extendTraces(graphDiv, {{
                    x: [['{new_timestamp}']],
                    y: [['{new_price}']]
                }}, [0]);
                console.log('Running update...')
            }} else {{
                console.error('Graph div not found.');
            }}
        """
            
            # Update the chart without reloading
            self.price_chart_widget.page().runJavaScript(js_code)

        except Exception as e:
            print(f"Error updating price chart incrementally: {e}")

    def create_sma_chart(self, events):
        """Create a Plotly chart for SMA and events."""
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=events['timestamps'], y=events['SMA'], mode='lines', name='SMA', line=dict(dash='dash',width=1)))
        fig.add_trace(go.Scatter(x=events['timestamps'], y=events['EMA'], mode='lines', name='EMA', line=dict(dash='dot')))
        fig.update_layout(
            title="SMA and Important Events",
            xaxis_title="Time",
            yaxis_title="Price",
            template="plotly_dark"
        )
        fig.update_layout(
            template="plotly_dark",  # Use the dark template
            paper_bgcolor="#1f2235",  # Outer graph area background
            plot_bgcolor="#1f2235",  # Plot area background
            xaxis=dict(
                title="Days",
                type="category",  # Treat x-axis as categorical data
            )
        )
        return fig

    def display_interactive_chart(self, fig):
        """Display an interactive Plotly chart."""
        # This function assumes you are using Plotly to embed the chart in a PyQt widget.
        # The implementation will depend on how you are embedding the chart.
        webview = QWebEngineView()
        # Embed the HTML with dynamic resizing
        custom_html = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
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
                <div id="graph"></div>
                <script>
                    // Reference the graph container
                    var graphDiv = document.getElementById('graph');

                    // Convert Python data to JavaScript
                    const data = {json.dumps(json.loads(fig.to_json())['data'])};
                    const layout = {json.dumps(json.loads(fig.to_json())['layout'])};

                    // Safely render or update the chart
                    if (typeof Plotly !== "undefined" && graphDiv) {{
                        Plotly.react(graphDiv, data, layout);
                    }}

                    // Adjust chart size dynamically
                    window.addEventListener('resize', () => {{
                        Plotly.relayout(graphDiv, {{
                        width: window.innerWidth,
                        height: window.innerHeight
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
        bottom_layout.addWidget(self.create_crypto_icon())
        bottom_layout.addWidget(self.create_correlation_matrix())
        return bottom_layout

    def create_daily_returns_table(self):
        # get data from backend
        data_ETH = CryptoAnalysis.calculate_daily_growth("ETH")
        data_index_zero = data_ETH["daily_growth"][0]
        data_index_one = data_ETH["daily_growth"][1]
        data_index_two = data_ETH["daily_growth"][2]
        """Create and return a table for daily returns."""
        table = self.create_table_widget(3, 2, ["Date", "Daily Growth (%)"], [
            [data_ETH["dates"][0], f"{data_index_zero}%"],
            [data_ETH["dates"][1], f"{data_index_one}%"],
            [data_ETH["dates"][2], f"{data_index_two}%"]
        ])
        return table
    
    def create_crypto_icon(self):
        """Create a QLabel with a simple icon for sentiment analysis."""
        sentiment_icon = QLabel()
        sentiment_icon.setAlignment(Qt.AlignCenter)
        sentiment_icon.setStyleSheet("background-color: #1a1b2f; padding: 10px")

        # Load a simple icon
        path = Helper.get_current_icon_directory()
        pixmap = QPixmap(f"{path}\\icons8-ethereum.png")  # Replace with the path to your icon file
        sentiment_icon.setPixmap(pixmap.scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation))

        return sentiment_icon

    def create_correlation_matrix(self):
        # get data from backend
        data = CryptoAnalysis.get_correlation_matrix(["BTC","ETH","BNB"])
        """Create and return a correlation matrix table."""
        correlation_matrix = self.create_table_widget(
            rows=3,
            cols=3,
            headers=["BTC", "ETH", "BNB"],
            vertical_headers=["BTC", "ETH", "BNB"],
            data=[
                [data["BTC"]["BTC"], data["BTC"]["ETH"], data["BTC"]["BNB"]],
                [data["ETH"]["BTC"], data["ETH"]["ETH"], data["ETH"]["BNB"]],
                [data["BNB"]["BTC"], data["BNB"]["ETH"], data["BNB"]["BNB"]]
            ]
        )
        return correlation_matrix

    def create_table_widget(self, rows, cols, headers, data, vertical_headers=None):
        """
        Create and return a QTableWidget populated with data.

        :param rows: Number of rows in the table.
        :param cols: Number of columns in the table.
        :param headers: List of column headers.
        :param data: 2D list containing the table data.
        :param vertical_headers: Optional list of custom vertical headers.
        """
        table = QTableWidget(rows, cols)
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
        table.setHorizontalHeaderLabels(headers)

        if vertical_headers:
            table.setVerticalHeaderLabels(vertical_headers)

        # Populate table with data
        for row in range(rows):
            for col in range(cols):
                value = data[row][col]
                # Check if the value is numeric, format it if it is
                item_text = f"{value:.2f}" if isinstance(value, (int, float)) else str(value)
                item = QTableWidgetItem(item_text)
                item.setTextAlignment(Qt.AlignCenter)
                table.setItem(row, col, item)
         # Resize rows to fit content
        table.resizeRowsToContents()

        # Calculate the total height of the table to fit the content
        total_height = table.horizontalHeader().height()
        for row in range(table.rowCount()):
            total_height += table.rowHeight(row)

        # Set the table's height to the calculated value
        table.setFixedHeight(total_height)

        # Set table properties
        table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        table.resizeColumnsToContents()
        table.horizontalHeader().setStretchLastSection(True)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        return table
    def adjust_text_edit_size(self, text_edit):
        """Adjust the size of a QTextEdit widget based on its content."""
        # Get the height of the document
        doc_height = text_edit.document().size().height()
        
        # Add some padding for aesthetic purposes
        total_height = int(doc_height + text_edit.contentsMargins().top() + text_edit.contentsMargins().bottom() + 80)

        # Set the fixed height of the widget based on content
        text_edit.setFixedHeight(total_height)

