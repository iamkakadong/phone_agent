from src.utils.typedef import AgentTask
from src.agents.agent import Agent
from src.live_audio_stream_handler.live_audio_stream_handler import LiveAudioStreamHandler
from src.utils.audio_stream import LiveAudioInputStream

import openai
import os


def main():
    stream_handler = LiveAudioStreamHandler(
        agent=Agent(AgentTask(name="Tianshu", goal="make a reservation at a restaurant")),
        input_stream=LiveAudioInputStream(sample_rate=44100),
        output_stream="Print",
        stream_poll_frequency=1,
        buffer_process_frequency=5
    )

    stream_handler.run_continuously()

if __name__ == "__main__":
    OPENAI_API_KEY = os.environ["OPENAI_API_KEY_PERSONAL"]
    openai.api_key = OPENAI_API_KEY

    main()