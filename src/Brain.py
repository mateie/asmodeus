import ollama
from typing import Any

from Util import Util
from Apps import Apps


MODEL = "qwen3:8b"

class Brain:
    def __init__(self):
        self.history = [{
            "role": "system",
            "content": "You are Asmodeus (Asmo for short), a concise, capable personal assistant running on the user's PC."
        }]
        self.think = False

        self.util = Util()
        self.apps = Apps(self.util)


    def turn(self):
        while True:
            stream = ollama.chat( # pyright: ignore[reportUnknownMemberType]
                model=MODEL, messages=self.history, tools=list(self.apps.tools.values()),
                think=self.think, stream=True, options={"num_ctx": 8192}
            )
            
            text: str = ""
            calls: list[Any] = []
            for chunk in stream:
                message = chunk.message
                
                if message.thinking:
                    continue
                
                if message.content:
                    if not text:
                        print("Asmo > ", end="", flush=True)
                        
                    text += message.content
                    print(message.content, end="", flush=True)
                    
                if message.tool_calls:
                    calls.extend(message.tool_calls)
                    
            entry: dict[str, Any] = {
                "role": "assistant", 
                "content": text
            }
            
            if calls:
                entry["tool_calls"] = [
                    {
                        "function": {
                            "name": call.function.name,
                            "arguments": call.function.arguments
                        },
                    }
                    for call in calls
                ]
        
            self.history.append(entry)
            
            if not calls:
                print("\n")
                return

            for call in calls:
                name, args = call.function.name, call.function.arguments
                
                try:
                    result = self.apps.tools[name](**args)
                except Exception as e:
                    result = f"Error: {e}"
                    
                self.history.append({
                    "role": "tool", 
                    "tool_name": name, 
                    "content": str(result)
                })
                       

    def run(self):
        while True:
            user = input("You > ")

            if user.lower().strip() == "":
                continue

            if user.lower() in ("exit", "quit"):
                break
            
            if user.lower() == "/think":
                self.think = not self.think
                print(f"Asmo > I am {'' if self.think else 'not '}thinking\n")
                continue
            
            self.history.append({
                "role": "user", 
                "content": user
            })

            self.turn()

