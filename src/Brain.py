import queue
import threading

import ollama
import re
from typing import Any

from Ears import Ears
from Files import Files
from Mouth import Mouth
from Util import Util
from Apps import Apps
from Web import Web


MODEL = "qwen3:8b"
GAMING_MODEL = "qwen3:4b"

SYSTEM_PROMPT = (
    "You are Asmodeus, Asmo for short, the user's assistant on their Windows PC. "
    "Talk like a sharp, dry-witted friend, not a customer service bot. "
    "Replies are spoken aloud, so keep them to one or two short sentences. "
    "No lists, no markdown, no emoji. Never say 'certainly', 'as an AI', or apologize "
    "unless something actually broke. Don't offer more help at the end. "
    "Use your tools to take actions instead of asking the user for file paths. "
    "The user's folders are named aliases like desktop, documents, notes, and workspace. "
    "For current events, prices, or anything you're unsure about, search the web instead of guessing."
)

class Brain:
    def __init__(self):
        self.history = [{
            "role": "system",
            "content": SYSTEM_PROMPT
        }]
        
        self.think = False
        self.gaming = False
        
        self.model = MODEL
        self.keep_alive = "5m"
        
        self.ears = Ears(True)
        self.mouth = Mouth()

        self.util = Util()
        self.apps = Apps(self.util)
        self.files = Files()
        self.web = Web()
        
        self.tools: dict[str, Any] = {
            **self.apps.tools, 
            **self.files.tools, 
            **self.web.tools
            }
        
        self.inbox: queue.Queue[str] = queue.Queue()
        self.idle = threading.Event()
        self.idle.set()

    def turn(self):
        while True:
            stream = ollama.chat( # pyright: ignore[reportUnknownMemberType]
                model=self.model, 
                messages=self.history, 
                tools=list(self.tools.values()),
                think=self.think, 
                stream=True, 
                options={"num_ctx": 8192},
                keep_alive=self.keep_alive
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
                self.mouth.speak(text)
                return

            for call in calls:
                name, args = call.function.name, call.function.arguments
                # print(f"[tool] {name}({args})")
                
                try:
                    if name not in self.tools:
                        result = f"Error: no tool named '{name}'. Available: {', '.join(self.tools)}" 
                    else:
                        result = self.tools[name](**args)
                except Exception as e:
                    result = f"Error: {e}"
                    
                # print(f"[result] {result}")
                    
                self.history.append({
                    "role": "tool", 
                    "tool_name": name, 
                    "content": str(result)
                })
                
    def listen_loop(self):
        while True:
            self.idle.wait()
            
            if not self.ears.wait_for_wake(self.idle):
                continue
            
            if not self.idle.is_set():
                continue
            
            self.mouth.acknowledge()
            user = self.ears.record()
            
            if user:
                print(f"You > {user}")
                self.inbox.put(user)
                
    def type_loop(self):
        while True:
            user = input("You > ").strip()
            
            if user:
                self.inbox.put(user)
                
    def set_gaming(self, on: bool):
        ollama.generate(model=self.model, keep_alive=0)
        
        self.gaming = on
        self.model = GAMING_MODEL if on else MODEL
        self.keep_alive = "30s" if on else "5m"
        
        reply = "Gaming mode is on" if on else "Gaming mode is off"
        print(f"Asmo > {reply}\n")
        self.mouth.speak(reply)
                
    def handle(self, user: str) -> bool:
        command = re.sub(r"[^a-z ]", "", user.lower()).strip()
        
        if command in ("shut down", "goodbye", "exit", "quit"):
            print("Asmo > Bye :<\n")
            return False
        
        if command in ("gaming on", "gaming off") or user.lower() == "/gaming":
            self.set_gaming(command == "gaming on" if command.startswith("gaming") else not self.gaming)
            return True

        if command in ("thinking on", "thinking off") or user.lower() == "/think":
            self.think = command == "thinking on" if command.startswith("thinking") else not self.think
            print(f"Asmo > I am {'' if self.think else 'not '}thinking\n")
            return True
        
        self.history.append({
            "role": "user", 
            "content": user
        })
        
        self.turn()
        return True
                       

    def run(self):
        print("Asmo > I am listening. Say 'hey asmo' or 'hey asmodeus' to wake me, or just type. Ctrl+C to quit.\n")
        
        threading.Thread(target=self.listen_loop, daemon=True).start()
        threading.Thread(target=self.type_loop, daemon=True).start()
        
        while True:
            try:
                user = self.inbox.get(timeout=0.5)
            except queue.Empty:
                continue
            
            self.idle.clear()
            try:
                if not self.handle(user):
                    break
            finally:
                self.idle.set()

