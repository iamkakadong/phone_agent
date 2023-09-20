from src.utils.typedef import AgentTask
from src.agents.agent import Agent
from src.live_audio_stream_handler.live_audio_stream_handler import LiveAudioStreamHandler
from src.utils.audio_stream import AudioStream
from soundfile import SoundFile
import sounddevice as sd

def test_live_audio_stream_handler():
    handler = LiveAudioStreamHandler(stream_poll_frequency=5)
    # stream = AudioStream('tests/jfk.flac')
    # handler.set_input_stream(stream)
    handler.start()

if __name__ == "__main__":
    test_live_audio_stream_handler()