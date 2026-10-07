import ollama

MODEL = "qwen3:8b"
history = [{
    "role": "system",
    "content": "You are Asmodeus (Asmo for short), a concise, capable personal assistant running on the user's PC."
}]
think = False

def main() -> None:
    global think
    while True:
        user = input("You > ")

        if user.lower().strip() == "":
            continue

        if user.lower() in ("exit", "quit"):
            break
        
        if user.lower() == "/think":
            think = not think
            print(f"Asmo > I am {'' if think else 'not '}thinking\n")
            continue

        history.append({"role": "user", "content": user})
        stream = ollama.chat(
            model=MODEL, messages=history, think=think, stream=True,
            options={"num_ctx": 8192}
        )

        text = ""
        print("Asmo > ", end="", flush=True)
        for chunk in stream:
            piece = chunk["message"]["content"]
            text += piece
            print(piece, end="", flush=True)
        print("\n")

        history.append({"role": "assistant", "content": text})
