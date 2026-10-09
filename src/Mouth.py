import numpy as np
from numpy.typing import NDArray
from piper import PiperVoice

import sounddevice as sd # pyright: ignore[reportMissingTypeStubs]
from pathlib import Path
import random
import re

VOICE = Path(__file__).parent / "models" / "voices" / "en_US-ryan-medium.onnx"
ACKS = ["Yes?", "Mhm?", "Yeah?", "What?", "Go on.", "I'm listening.", "Huh?", "What is it?", "Yes, I'm here.", "Yes, go ahead.", "Yes, what is it?"]

class Mouth:
    def __init__(self):
        self.voice = PiperVoice.load(VOICE)
        self.rate = 22050
        self.acks = [self.render(text) for text in ACKS]
        
    def render(self, text: str) -> NDArray[np.int16]:
        parts: list[NDArray[np.int16]] = []
        for chunk in self.voice.synthesize(text):
            self.rate = chunk.sample_rate
            parts.append(chunk.audio_int16_array)
            
        return np.concatenate(parts) if parts else np.zeros(0, dtype=np.int16)
    
    def play(self, audio: NDArray[np.int16]):
        if audio.size:
            sd.play(audio, self.rate) # pyright: ignore[reportUnknownMemberType]
            sd.wait()
            
    def acknowledge(self):
        self.play(random.choice(self.acks))
        
    def speak(self, text: str):
        text = re.sub(r"https?://\S+|[*`#>~]", "", text)
 
        for sentence in re.split(r"(?<=[.!?])\s+", text.strip()):
            if sentence:
                self.play(self.render(sentence))