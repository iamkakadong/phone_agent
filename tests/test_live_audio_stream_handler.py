from src.agent import Agent, Task
from src.services import LiveAudioStreamHandler
from src.stream import AudioStream
from soundfile import SoundFile
import sounddevice as sd

def test_live_audio_stream_handler():
    handler = LiveAudioStreamHandler(poll_frequency=5)
    # stream = AudioStream('tests/jfk.flac')
    # handler.set_input_stream(stream)
    handler.start()

if __name__ == "__main__":
    test_live_audio_stream_handler()