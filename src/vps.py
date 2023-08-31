from src.stream import AudioStream


class VirtualPhoneService:
    def __init__(self) -> None:
        pass

    def call(self, number):
        pass

    def hangup(self):
        pass

    def play(self, voice):
        pass

    def press_keys(self, keys):
        pass

    def get_audio_stream(self) -> AudioStream:
        return None
    
    def get_status(self):
        return None