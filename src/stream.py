from typing import Optional
from src.typedef import Action
import pyaudio
from soundfile import SoundFile
import sounddevice as sd
import numpy as np


def audio_callback(indata, frames, time, status):
    volume_norm = np.linalg.norm(indata)*10
    print('|' * int(volume_norm))  # Show the audio level

def get_audio_stream(block_size, mic_name='Loopback Audio', callback_func=None):
    devices = sd.query_devices()
    device_id = None
    for device in devices:
        if device['name'] == mic_name and device['max_input_channels'] > 0:
            device_id = device['index']
            break

    if device_id is None:
        print(f"No microphone found by the name of '{mic_name}'")
    else:
        stream = sd.InputStream(device=device_id, blocksize=block_size, channels=2, callback=callback_func)
        return stream


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