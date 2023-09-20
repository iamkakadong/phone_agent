from src.utils.typedef import AgentTask

import openai

from typing import List, Tuple


class Agent:
    def __init__(self, task: AgentTask) -> None:
        self.chat_history: List[Tuple[str, str]] = []
        self.task = task

    def _gen_system_prompt(self):
        return f"""
            You are a helpful assistant that makes phone call for people to achieve their goals. You will be receiving a live transcript of the phone call and should respond to the conversation.
            Your specific goal is to help {self.task.name} {self.task.goal}.
            You are going to speak on behalf of {self.task.name}.
        
            Keep the following rules in mind:
            - Please only respond to the current conversation for {self.task.name}. DO NOT generate any response for the other person over the phone. 
            - Since you are receiving a live transcript from the phone call, sometimes a sentence may not be completed yet. In that case, you should simply output [NO_ACTION].
            - When you have achieved the goal and is ready to hang up, just output [END_CALL] at the end of your response.
        """

    def get_response(self, human_message: str) -> str:
        """
            Returns the response from the agent given the human message
        """
        human_message = f"""Phone: {human_message}
            You: """
        messages = self._construct_chat_messages_from_history()
        messages.append({"role": "user", "content": human_message})

        llm_response = self._get_response_from_llm(messages)

        if llm_response == "[NO_ACTION]":
            pass
        elif llm_response.count("[END_CALL]") > 0:
            self.chat_history.append(("user", human_message))
            self.chat_history.append(("system", llm_response))
        else:
            self.chat_history.append(("user", human_message))
            self.chat_history.append(("system", llm_response))
        return llm_response


    def _construct_chat_messages_from_history(self) -> str:
        """
            Constructs the chat messages from the chat history list
        """
        messages = [
            {"role": "system", "content": self._gen_system_prompt()},
        ]
        for role, message in self.chat_history:
            messages.append({"role": role, "content": message})
        return messages

    def _get_response_from_llm(self, messages: List[dict]) -> str:
        """
            Returns the response from the language model given the chat messages
        """
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.0
        )
        return response.choices[0].message.content

    def clear_history(self):
        self.chat_history = []