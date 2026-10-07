from datetime import datetime

class Util:
    def get_time(self) -> str:
        return datetime.now().strftime("%A, %B %d %Y, %I:%M %p")

    