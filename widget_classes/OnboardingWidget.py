from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QStackedWidget, QLabel, QSizePolicy
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import Qt
import numpy as np
import plotly.graph_objects as go
from backend.home.fan_chart_data import CryptoFanChartGenerator


class OnboardingWidget(QWidget):
    def __init__(self):
        super().__init__()
        
        # Set border style
        self.setStyleSheet("""
            OnboardingWidget {
                border: 3px solid teal;
                border-radius: 10px;
                background-color: #2c2f45;
            }
        """)
        self.setMinimumSize(500, 350)  # Set width and height
        # Main layout
        layout = QVBoxLayout(self)

        # Add navigation indicators
        self.dots_layout = QHBoxLayout()
        self.dots_layout.setAlignment(Qt.AlignCenter)
        layout.addLayout(self.dots_layout)

        # Add stacked widget for onboarding screens
        self.stacked_widget = QStackedWidget()
        layout.addWidget(self.stacked_widget)

        # Add navigation buttons
        self.nav_layout = QHBoxLayout()
        self.nav_layout.setAlignment(Qt.AlignJustify)
        layout.addLayout(self.nav_layout)

        self.back_button = QPushButton("<")
        self.style_button(self.back_button)
        self.back_button.clicked.connect(self.previous_screen)
        self.nav_layout.addWidget(self.back_button, alignment=Qt.AlignLeft)

        self.next_button = QPushButton(">")
        self.style_button(self.next_button)
        self.next_button.clicked.connect(self.next_screen)
        self.nav_layout.addWidget(self.next_button, alignment=Qt.AlignRight)

        # Initialize screens
        self.num_screens = 3
        self.current_screen = 0
        self.init_screens()

        # Update indicators for the first screen
        self.update_indicators()

        self.setLayout(layout)

    def init_screens(self):
        # Example data for cryptocurrencies
        crypto_symbols = ["BTC", "ETH", "BNB"]

        for i, symbol in enumerate(crypto_symbols):
            screen = QWidget()
            screen_layout = QVBoxLayout()
            screen.setLayout(screen_layout)

            # Fetch fan chart data from the backend
            fan_chart_generator = CryptoFanChartGenerator()
            fan_chart_data = fan_chart_generator.generate_fan_chart(symbol)

            # Add chart to the screen layout
            chart_view = QWebEngineView()
            chart_view.setAttribute(Qt.WA_TranslucentBackground, True)
            chart_view.setStyleSheet("background: transparent;")
            chart_view.page().setBackgroundColor(Qt.transparent)
            chart_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

            # Generate and load HTML
            chart_html = self.generate_fan_chart_html(fan_chart_data)
            chart_view.setHtml(chart_html)
            screen_layout.addWidget(chart_view)

            # Add cryptocurrency label
            crypto_label = QLabel(f"{fan_chart_data['cryptocurrency']} Projection")
            crypto_label.setAlignment(Qt.AlignCenter)
            crypto_label.setStyleSheet("font-size: 20px; color: white;")
            screen_layout.addWidget(crypto_label)

            self.stacked_widget.addWidget(screen)

            # Create dots for indicators
            dot = QLabel("●")
            dot.setStyleSheet("font-size: 24px; color: gray;")
            self.dots_layout.addWidget(dot)


    def style_button(self, button):
        """Style navigation buttons."""
        button.setStyleSheet("""
            QPushButton {
                font-size: 20px;
                color: teal;
                background-color: #1f2235;
                border-radius: 15px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #2c2f45;
            }
        """)
        button.setFixedSize(50, 50)

    def generate_fan_chart_html(self, fan_chart_data):
        """
        Generate a responsive Plotly fan chart HTML using the provided data structure.
        """
        # Extract actual and projection data
        x_actual = fan_chart_data["actual_data"]["timestamps"]
        y_actual = fan_chart_data["actual_data"]["values"]

        x_fan = fan_chart_data["projection_data"]["timestamps"]
        y_mean = fan_chart_data["projection_data"]["mean"]
        confidence_intervals = fan_chart_data["projection_data"]["confidence_intervals"]

        # Create traces for the actual data
        traces = [
            go.Scatter(
                x=x_actual,
                y=y_actual,
                mode='lines',
                name='Actual',
                line=dict(color='blue')
            )
        ]

        # Add confidence intervals
        for ci in confidence_intervals:
            traces.append(go.Scatter(
                x=np.concatenate([x_fan, x_fan[::-1]]),
                y=np.concatenate([ci["upper"], ci["lower"][::-1]]),
                fill='toself',
                fillcolor=f'rgba(255, 0, 0, {0.2 / ci["ci"]})',
                line=dict(color='rgba(255,255,255,0)'),
                hoverinfo='skip',
                name=f"CI ±{ci['ci']}"
            ))

        # Add the mean projection line
        traces.append(go.Scatter(
            x=x_fan,
            y=y_mean,
            mode='lines',
            name='Mean Projection',
            line=dict(color='red', dash='dash')
        ))

        # Create the Plotly figure
        fig = go.Figure(data=traces)
        fig.update_layout(
            title=f"{fan_chart_data['cryptocurrency']} Fan Chart",
            template="plotly_dark",
            paper_bgcolor="#1f2235",
            plot_bgcolor="#1f2235",
            margin=dict(l=10, r=10, t=30, b=10),  # Minimize margins
            showlegend=True
        )

        # Generate responsive HTML
        html_content = fig.to_html(include_plotlyjs='cdn')
        responsive_html = f"""
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
                            width: 100%;
                            height: 100%;
                            overflow: hidden;
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
        return responsive_html


    def next_screen(self):
        """Go to the next screen."""
        if self.current_screen < self.num_screens - 1:
            self.current_screen += 1
            self.stacked_widget.setCurrentIndex(self.current_screen)
            self.update_indicators()

    def previous_screen(self):
        """Go to the previous screen."""
        if self.current_screen > 0:
            self.current_screen -= 1
            self.stacked_widget.setCurrentIndex(self.current_screen)
            self.update_indicators()

    def update_indicators(self):
        """Update the dots to indicate the current screen."""
        for i in range(self.dots_layout.count()):
            dot = self.dots_layout.itemAt(i).widget()
            if i == self.current_screen:
                dot.setStyleSheet("font-size: 24px; color: white;")
            else:
                dot.setStyleSheet("font-size: 24px; color: gray;")


#fanchart data ==> generate fan chart
    # def fetch_crypto_data(crypto_symbol):
    #     """Fetch fan chart data for a given cryptocurrency from the backend."""
    #     # Replace with actual backend API call
    #     response = backend.get_fan_chart_data(crypto_symbol)
    #     return response  # Assuming the backend sends data in the structure above


"""data structure needed to fill the data"""

# {
#     "cryptocurrency": "Bitcoin",
#     "actual_data": {
#         "timestamps": ["2024-11-27 10:00", "2024-11-27 10:01", "2024-11-27 10:02"],
#         "values": [50000, 50100, 50250]
#     },
#     "projection_data": {
#         "timestamps": ["2024-11-27 10:03", "2024-11-27 10:04", "2024-11-27 10:05"],
#         "mean": [50300, 50400, 50550],
#         "confidence_intervals": [
#             {"ci": 0.5, "upper": [50350, 50450, 50600], "lower": [50250, 50350, 50500]},
#             {"ci": 1, "upper": [50400, 50500, 50650], "lower": [50200, 50300, 50500]}
#         ]
#     }
# }
