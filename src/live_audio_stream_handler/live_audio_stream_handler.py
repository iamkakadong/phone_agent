import threading
import time
from src.agents.agent import Agent
from src.utils.transcriber import Transcriber
from src.utils.audio_stream import LiveAudioInputStream
from src.utils.typedef import Action


import numpy as np
import sounddevice as sd


class LiveAudioStreamHandler:
    """
        An object that listens to a live audio stream (i.e. phone call) and publishes responses accordingly
    """
    STREAM_MAX_SIZE = 20 # in seconds
    def __init__(self, agent: Agent = None, input_stream: LiveAudioInputStream = None, output_stream: str = "Print", stream_poll_frequency=1, buffer_process_frequency=1) -> None:
        self.agent: Agent = agent
        self.input_stream: LiveAudioInputStream = input_stream
        self.output_stream: str = output_stream
        self.stream_poll_frequency = stream_poll_frequency # in seconds

        self.lock = threading.Lock()
        self.buffer: np.ndarray = None
        self.buffer_internal: np.ndarray = None
        self.buffer_process_frequency = buffer_process_frequency # in seconds

        self.counter = 0

    def run_continuously(self, max_timeout=STREAM_MAX_SIZE):
        if not self._check_is_ready():
            # TODO: throw an exception
            pass
        
        # print("Starting threads")
        t1 = threading.Thread(target=self._process_input_stream_thread, args=(self.stream_poll_frequency, max_timeout))
        t2 = threading.Thread(target=self._process_buffer_thread, args=(self.buffer_process_frequency,))

        # print("Starting threads")
        t1.start()
        t2.start()

        t1.join()
        t2.join()

    def _process_input_stream_thread(self, poll_frequency, max_timeout):
        print("Starting input stream")
        input_stream = self.input_stream.get_audio_stream(callback_freq=poll_frequency, callback_func=self._on_callback)
        with input_stream:
            sd.sleep(max_timeout * 1000)

    def _process_buffer_thread(self, frequency):
        print("Starting buffer processing")
        while True:
            # sleep for frequency seconds
            time.sleep(frequency)
            self._process_buffer()

    def _check_is_ready(self):
        if self.input_stream is None:
            return False
        return True

    def _on_callback(self, indata, frames, time, status):
        self.lock.acquire()
        if self.buffer is None:
            self.buffer = indata
        else:
            self.buffer = np.concatenate((self.buffer, indata), axis=0)
        self.lock.release()

        # This step can cause latency such that there is significant gap between two blocks coming out of audio stream
        # It's better to use a separate thread for this such that it doesn't block the audio stream
        # Also, it's better for the callback to just put the data in buffer and let the other thread handle its processing
        # transcribed_text = Transcriber.transcribe(self.buffer, self.counter)
        # self.counter += 1

        # action = self.gen_action(transcribed_text)
        # if action is not None:
        #     self.buffer = None
        #     self.publish_action(action)

    def _process_buffer(self):
        self.lock.acquire()
        if self.buffer is None:
            return
        else:
            buffer_copy = self.buffer.copy()
            self.buffer = None
        self.lock.release()

        if self.buffer_internal is None:
            self.buffer_internal = buffer_copy
        else:
            self.buffer_internal = np.concatenate((self.buffer_internal, buffer_copy), axis=0)

        transcribed_text = Transcriber.transcribe(self.buffer_internal, self.counter)
        self.counter += 1

        action = self.gen_action(transcribed_text)
        if action is not None:
            self.buffer_internal = None
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

    def set_output_channel(self, channel):
        self.output_stream = channel

    def get_output_stream(self):
        return self.output_stream

    def publish_action(self, action):
        if self.output_stream == "Print":
            print(action)
        return