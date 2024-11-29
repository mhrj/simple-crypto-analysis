import os

class Helper():
    def __init__(self):
        super().__init__()
        
    def get_current_icon_directory():
        directory = os.getcwd()
        icon_path = os.path.join(directory, "icons")
        return icon_path