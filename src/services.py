from dataclasses import dataclass
import time
from src.agent import Agent
from src.stream import ActionStream, AudioStream, get_audio_stream
from src.typedef import Action, Task
from src.vps import VirtualPhoneService
import sounddevice as sd
import numpy as np


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
        

class Transcriber:
    @staticmethod
    def transcribe(audio: np.ndarray, counter=None) -> str:
        from scipy.io.wavfile import write
        import openai
        write(f"tmp/temp_{counter}.wav", 44100, audio)
        audio_file = open(f"tmp/temp_{counter}.wav", 'rb')
        # transcript = openai.Audio.transcribe("whisper-1", audio_file)
        transcript = {'text': 'Hello, how are you?'}
        return transcript['text']


class LiveAudioStreamHandler:
    """
        An object that listens to a live audio stream (i.e. phone call) and publishes responses accordingly
    """
    STREAM_MAX_SIZE = 20 # in seconds
    def __init__(self, agent: Agent = None, input_stream: sd.InputStream = None, output_stream: ActionStream = None, poll_frequency=1) -> None:
        self.input_stream: sd.InputStream = input_stream # Audio Stream
        self.output_stream: ActionStream = output_stream if output_stream else ActionStream() # Action Stream
        self.agent: Agent = agent
        self.poll_frequency = poll_frequency # in seconds
        self.buffer: np.ndarray = None
        self.counter = 0

    def start(self):
        self.status = "running"
        if self.input_stream is None:
            self.input_stream = get_audio_stream(block_size=self.poll_frequency * 44100, callback_func=self.on_callback)
        with self.input_stream:
            # stream is active and callback is working
            sd.sleep(self.STREAM_MAX_SIZE * 1000)
    
    def on_callback(self, indata, frames, time, status):
        # print("On callback")
        if self.buffer is None:
            self.buffer = indata
        else:
            self.buffer = np.concatenate((self.buffer, indata), axis=0)
        
        # This step can cause latency such that there is significant gap between two blocks coming out of audio stream
        # It's better to use a separate thread for this such that it doesn't block the audio stream
        # Also, it's better for the callback to just put the data in buffer and let the other thread handle its processing
        transcribed_text = Transcriber.transcribe(self.buffer, self.counter)
        self.counter += 1

        action = self.gen_action(transcribed_text)
        if action is not None:
            self.buffer = None
            self.publish_action(action)

    def gen_action(self, transcribed_text):
        action = transcribed_text
        if self.agent is not None:
            # response = self.agent.get_response(transcribed_text)
            # action = self.parse_response(response)
            pass
        return action

    def parse_response(self, response: str):
        if response == "[NO_ACTION]":
            return None
        elif response.count("[END_CALL]") > 0:
            # TODO: Respond voice before hangup
            return Action(type="hangup")
        elif response.count("[RESPOND_VOICE]") > 0:
            return Action(type="respond_voice", voice=response.replace("[RESPOND_VOICE]", ""))
        elif response.count("[RESPOND_KEYPAD]") > 0:
            return Action(type="respond_keypad", keys=response.replace("[RESPOND_KEYPAD]", ""))
        else:
            raise Exception(f"Invalid response: {response}")

    def stop(self):
        self.status = "stopped"

    def set_input_stream(self, stream):
        self.input_stream = stream

    def get_output_stream(self):
        return self.output_stream
    
    def publish_action(self, action):
        # self.output_stream.put(action)
        print(action)


        