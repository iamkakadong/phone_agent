from dataclasses import dataclass
import time
from src.stream import ActionStream, AudioStream
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
    def transcribe(audio: np.ndarray) -> str:
        from scipy.io.wavfile import write
        import openai
        write("tmp/temp.wav", 44100, audio)
        audio_file = open("tmp/temp.wav", 'rb')
        transcript = openai.Audio.transcribe("whisper-1", audio_file)
        return transcript['text']


class LiveAudioStreamHandler:
    """
        An object that listens to a live audio stream (i.e. phone call) and responds to the it accordingly
    """
    def __init__(self, agent, input_stream: AudioStream = None, output_stream: ActionStream = None) -> None:
        self.input_stream: AudioStream = input_stream # Audio Stream
        self.output_stream: ActionStream = output_stream if output_stream else ActionStream() # Action Stream
        self.agent: Agent = agent
        self.poll_frequency = 1 # in seconds
        self.buffer: np.ndarray = None

    def start(self):
        self.status = "running"
        while self.status == "running":
            # poll every 1 second
            time.sleep(self.poll_frequency)

            context = self.input_stream.poll(self.poll_frequency)
            # TODO: Handle case when context is empty

            if self.buffer is None:
                self.buffer = context
            else:
                self.buffer = np.concatenate((self.buffer, context), axis=0)
            
            # For testing only
            # sd.play(self.buffer, self.input_stream.stream.samplerate)
            
            transcribed_text = Transcriber.transcribe(self.buffer)
            print(transcribed_text)
            action = self.agent.get_action(transcribed_text)
            if action is not None:
                self.buffer = None
                self.publish_action(action)

    def stop(self):
        self.status = "stopped"

    def set_input_stream(self, stream):
        self.input_stream = stream

    def get_output_stream(self):
        return self.output_stream
    
    def publish_action(self, action):
        self.output_stream.put(action)
        print(action)


class Agent:
    def __init__(self) -> None:
        self.internal_knowledge = None
        self.external_knowledge = None
        self.goal = None
        pass

    def set_goal(self, goal):
        self.goal = goal
    
    def query_external_knowledge(self, query):
        pass

    def query_internal_knowledge(self, query):
        pass

    def update_internal_knowledge(self, query):
        pass

    def update_context(self, context):
        pass

    def get_action(self, context) -> Action:
        """
            The context will be passed in sequentially
        """
        self.update_context(context)
        if self.should_respond():
            return self.generate_action_internal()
        else:
            return None # TODO: return an empty action
        
    def should_respond(self):
        pass

    def generate_action_internal(self):
        pass
        