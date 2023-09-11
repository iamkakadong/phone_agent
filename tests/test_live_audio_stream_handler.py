from src.agent import Agent, Task
from src.services import LiveAudioStreamHandler
from src.stream import AudioStream
from soundfile import SoundFile
import sounddevice as sd

def test_live_audio_stream_handler():
    handler = LiveAudioStreamHandler(Agent(task=Task(name='Tianshu', goal='make a restaurant reservation')))
    # stream = AudioStream('tests/jfk.flac')
    # handler.set_input_stream(stream)
    handler.start()

if __name__ == "__main__":
    test_live_audio_stream_handler()