from src.agents.agent import Agent
from src.live_audio_stream_handler.live_audio_stream_handler import LiveAudioStreamHandler
from src.utils.audio_stream import AudioStream
from src.utils.typedef import Task


import time


class PhoneCallService:
    """
        This is the main service that connects various components together
    """
    def __init__(self) -> None:
        self.vps = VirtualPhoneService()
        self.agent = Agent()
        self.live_audio_stream_handler = LiveAudioStreamHandler(self.agent)

    def run_task(self, task: Task):
        """
            Runs a task on the virtual phone service
        """
        self.agent.set_goal(task.goal)
        self.live_audio_stream_handler.set_input_stream(self.vps.get_audio_stream())
        self.action_stream = self.live_audio_stream_handler.get_output_stream()
        self.live_audio_stream_handler.start()
        self.vps.call(task.number)
        self.run_continuously()

    def run_continuously(self):
        while self.vps.status != "hangup":
            time.sleep(1)
            action = self.action_stream.poll()
            if action.type == "hangup":
                self.vps.hangup()
            elif action.type == "respond_voice":
                self.vps.play(action.voice)
            elif action.type == "respond_keypad":
                self.vps.press_keys(action.keys)


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