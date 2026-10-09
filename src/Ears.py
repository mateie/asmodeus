from pathlib import Path
from typing import Any, cast

from faster_whisper import WhisperModel # pyright: ignore[reportMissingTypeStubs]
import numpy as np
import sounddevice as sd # pyright: ignore[reportMissingTypeStubs]
from numpy.typing import NDArray
from openwakeword.model import Model # pyright: ignore[reportMissingTypeStubs]
from openwakeword import utils # pyright: ignore[reportMissingTypeStubs]

WAKE_MODEL = Path(__file__).parent / "models" / "hey_asmo.onnx"

THRESHOLD = 0.35
SILENCE_RMS = 500.0
HITS = 2

RATE = 16000
CHUNK = 1280
MAX_SECONDS = 10
SILENCE_CHUNKS = 15

def read_chunk(stream: Any) -> NDArray[np.int16]:
    data = cast(NDArray[np.int16], stream.read(CHUNK)[0])
    return data.flatten()

class Ears:
    def __init__(self, debug: bool = False):
        utils.download_models(["no_pretrained_models"]) # Needed
    
        self.debug = debug
        
        self.wake: Any = Model(wakeword_models=[str(WAKE_MODEL)], inference_framework="onnx")
        self.whisper = WhisperModel("small.en", device="cpu", compute_type="int8")
        
    def wait_for_wake(self):
        """Block until the wake word is heard."""
 
        self.wake.reset()
        
        hits = 0
 
        with sd.InputStream(samplerate=RATE, channels=1, dtype="int16", blocksize=CHUNK) as stream:
            while True:
                scores = cast(dict[str, float], self.wake.predict(read_chunk(stream)))
                top = max(scores.values())
 
                if self.debug and top > 0.1:
                    print(f"Wake score: {top:.3f}")
 
                hits = hits + 1 if top > THRESHOLD else 0
                if hits >= HITS:
                    break
                
    def record(self) -> str:
        """Record until you stop talking, return the transcript."""
        
        print("Asmo > (listening...)", flush=True)
        
        frames: list[NDArray[np.int16]] = []
        heard_speech = False
        silent = 0
        
        with sd.InputStream(samplerate=RATE, channels=1, dtype="int16", blocksize=CHUNK) as stream:
            for _ in range(int(MAX_SECONDS * RATE / CHUNK)):
                chunk = read_chunk(stream)
                frames.append(chunk)
                rms = float(np.sqrt(np.mean(chunk.astype(np.float32) ** 2)))
                if rms >= SILENCE_RMS:
                    heard_speech = True
                    silent = 0
                elif heard_speech:
                    silent += 1
                    if silent >= SILENCE_CHUNKS:
                        break
 
        if not heard_speech:
            return ""
        
        audio: NDArray[np.float32] = np.concatenate(frames).astype(np.float32) / 32768.0
        segments, _ = self.whisper.transcribe(audio, language="en", vad_filter=True) # pyright: ignore[reportUnknownMemberType]
        
        return " ".join(segment.text.strip() for segment in segments).strip()