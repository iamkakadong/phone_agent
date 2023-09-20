import sounddevice as sd

class LiveAudioInputStream:
    def __init__(self, sample_rate, mic_name='Loopback Audio') -> None:
        self.sample_rate = sample_rate
        self.mic_name = mic_name

    def get_audio_stream(self, 
                         callback_freq, # in seconds
                         callback_func):
        devices = sd.query_devices()
        device_id = None
        for device in devices:
            if device['name'] == self.mic_name and device['max_input_channels'] > 0:
                device_id = device['index']
                break

        if device_id is None:
            print(f"No microphone found by the name of '{self.mic_name}'")
        else:
            stream = sd.InputStream(device=device_id, blocksize=self.sample_rate * callback_freq, channels=2, callback=callback_func)
            return stream