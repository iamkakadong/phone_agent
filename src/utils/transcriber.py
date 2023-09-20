import numpy as np
import openai


class Transcriber:
    @staticmethod
    def transcribe(audio: np.ndarray, counter=None) -> str:
        from scipy.io.wavfile import write
        write(f"tmp/temp_{counter}.wav", 44100, audio)
        audio_file = open(f"tmp/temp_{counter}.wav", 'rb')
        transcript = openai.Audio.transcribe("whisper-1", audio_file)
        # transcript = {'text': 'Hello, how are you?'}
        return transcript['text']