import os
from pathlib import Path

from Util import Util


class Apps:
    def __init__(self, util: Util):
        self.apps = self.scan_start_menu()

        self.tools = {f.__name__: f for f in (util.get_time, self.open_app)}
        
        
    def scan_start_menu(self) -> dict[str, str]:
        roots = [
            Path(os.environ["PROGRAMDATA"]) / "Microsoft" / "Windows" / "Start Menu" / "Programs",
            Path(os.environ["APPDATA"]) / "Microsoft" / "Windows" / "Start Menu" / "Programs"
        ]
        found: dict[str, str] = {}
        for root in roots:
            for lnk in root.rglob("*.lnk"):
                if "uninstall" in lnk.stem.lower():
                    continue
                
                found[lnk.stem.lower()] = str(lnk)
        return found
        
    
    def open_app(self, app_name: str) -> str:
        """Opens an application by its name."""
    
        name = app_name.lower().strip()
        exe = self.apps.get(name)
        
        if not exe:
            matches = [n for n in self.apps if name in n]
            if matches:
                exe = self.apps[min(matches, key=len)]
        
        if not exe:
            return f"App '{app_name}' not found."
        
        try:
            os.startfile(exe)
            return f"Opened {app_name}."
        except Exception as e:
            return f"Failed to open {app_name}: {e}"