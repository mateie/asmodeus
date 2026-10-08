from pathlib import Path

class Files:
    def __init__(self):
        home = Path.home()
        self.folders = {
            "workspace": home / "AsmoFiles",
            "documents": home / "Documents",
            "desktop": home / "Desktop",
        }
        
        for p in self.folders.values():
            p.mkdir(parents=True, exist_ok=True)
            
        self.tools = {f.__name__: f for f in (self.list_files, self.read_file, self.write_file)}
        
    def safe(self, folder: str, path: str) -> Path:
        base = self.folders.get(folder.lower())
        if base is None:
            raise ValueError(f"Unknown folder: {folder}")
        
        full = (base / path).resolve()
        
        if not full.is_relative_to(base.resolve()):
            raise ValueError(f"Access to {full} is not allowed.")
        
        return full
    
    def list_files(self, folder: str = "workspace", subfolder: str = ".") -> str:
        """List the files in a folder.
        
        Args:
            folder: Must be exactly one of: workspacce, documents,  desktop.
            subfolder: A subfolder within the specified folder. Defaults to the root of the folder.
        """
        
        try:
            items = sorted(p.name + ("/" if p.is_dir() else "") for p in self.safe(folder, subfolder).iterdir())
            return "\n".join(items) or "(empty)"
        except Exception as e:
            return f"Error: {e}"
        
    def read_file(self, folder: str, filename: str) -> str:
        """Read a text file
        
        Args:
            folder: Must be exactly one of: workspacce, documents, desktop.
            filename: The name of the file to read, like "notes.txt" or "subfolder/notes.txt".
        """
        
        try:
            return self.safe(folder, filename).read_text(encoding="utf-8")[:4000]
        except Exception as e:
            return f"Error: {e}"
        
    def write_file(self, folder: str, filename: str, content: str) -> str:
        """Create a new text file.

        Args:
            folder: Where to save it. Must be exactly one of: workspace, documents, desktop.
            filename: Name of the file, like notes.txt. Add .txt if no extension was given.
            content: The text to write into the file.
        """

        try:
            if not Path(filename).suffix:
                filename += ".txt"
            target = self.safe(folder, filename)
            if target.exists():
                return f"{filename} already exists. Ask the user whether to overwrite it."
            
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
            return f"Wrote to {filename} in {folder}."
        except Exception as e:
            return f"Error: {e}"