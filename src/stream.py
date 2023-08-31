from typing import Optional
from src.typedef import Action
import pyaudio
from soundfile import SoundFile
import numpy as np


class AudioStream:
    def __init__(self, filepath: Optional[str] = None) -> None:
        self.stream = None
        if filepath is not None:
            self.set_stream_from_file(filepath)
        # self.stream: pyaudio.Stream = None
        # self.stream_rate = 44100 # ideally this should be accessible from the stream itself

    def set_stream_from_file(self, filepath: str):
        self.stream = SoundFile(filepath)

    def poll(self, poll_seconds: int) -> np.ndarray:
        return self.stream.read(poll_seconds * self.stream.samplerate)

class ActionStream:
    def __init__(self) -> None:
        pass

    def put(self, action: Action):
        pass

    def poll(self) -> Action:
        pass