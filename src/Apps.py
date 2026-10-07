import os

from Util import Util


class Apps:
    def __init__(self, util: Util):
        self.apps = {
            "notepad": "notepad.exe",
            "calculator": "calc.exe",
            "spotify": "spotify:"
        }

        self.tools = {f.__name__: f for f in (util.get_time, self.open_app)}
        
    
    def open_app(self, app_name: str) -> str:
        exe = self.apps.get(app_name.lower())
        if not exe:
            return f"App '{app_name}' not found."
        
        try:
            os.startfile(exe)
            return f"Opened {app_name}."
        except Exception as e:
            return f"Failed to open {app_name}: {e}"