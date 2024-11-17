import os

class Helper():
    def __init__(self):
        super().__init__()
        
    def create_chart_path(chart_name):
        directory = os.getcwd()
        chart_path = os.path.join(directory, "graphs", f"{chart_name}").replace("\\", "/")
        return chart_path