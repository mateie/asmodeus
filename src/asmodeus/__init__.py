import ollama

MODEL = "qwen3:8b"
history = [{
    "role": "system",
    "content": "You are Asmodeus (Asmo for short), a concise, capable personal assistant running on the user's PC."
}]
think = False

def main() -> None:
    while True:
        user = input("you > ")
        if user.lower() in ("exit", "quit"):
            break
        
        if user.lower() == "/think":
            think = not think
            print(f"[thinking {'on' if think else 'off'}]\n")
            continue

        history.append({"role": "user", "content": user})
        stream = ollama.chat(
            model=MODEL, messages=history, think=think, stream=True,
            options={"num_ctx": 8192}
        )

        text = ""
        print("asmo > ", end="", flush=True)
        for chunk in stream:
            piece = chunk["message"]["content"]
            text += piece
            print(piece, end="", flush=True)
        print("\n")

        history.append({"role": "assistant", "content": text})
