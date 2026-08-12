import json
from threading import Thread

import requests
import wx

from Constants import Strings


class LLMThread(Thread):
    """
    Thread for talking to LLM.
    """

    def __init__(self,
                 parent,
                 user_prompt: str,
                 system_prompt: str,
                 llm_url: str,
                 llm_tokens: int,
                 llm_responses: int,
                 llm_frequency_p: float,
                 llm_presence_p: float,
                 llm_temperature: float,
                 llm_verbosity: str) -> None:
        """
        Thread constructor.
        :param parent: The Frame that called the thread.
        :param user_prompt: Prompt.
        :param system_prompt: System prompt.
        :param llm_url: LLM REST api point compatible with open AI.
        :param llm_tokens: Max number of tokens to generate.
        :param llm_responses: Number of responses to generate.
        :param llm_frequency_p: Positive values penalize new tokens based on their existing frequency in the text so far, decreasing the model’s likelihood to repeat the same line verbatim.
        :param llm_presence_p: Positive values penalize new tokens based on whether they appear in the text so far, increasing the model’s likelihood to talk about new topics.
        :param llm_temperature: Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic.
        :param llm_verbosity: low, medium, high
        :return: None
        """
        super().__init__()
        self._parent = parent
        self._prompt = user_prompt
        self._system_prompt = system_prompt
        self._llm_url = llm_url

        self._llm_tokens = llm_tokens
        self._llm_responses = llm_responses
        self._llm_frequency_p = llm_frequency_p
        self._llm_presence_p = llm_presence_p
        self._llm_temperature = llm_temperature
        self._llm_verbosity = llm_verbosity
        self.start()

    def run(self) -> None:
        """
        Send a prompt to LLM on url and get a string response.
        :return: None
        """
        # This does not retain context, that would have to be passed along inside messages.
        messages = [{"role": "system", "content": self._system_prompt},
                    {"role": "user", "content": self._prompt}]
        try:
            response = requests.post(self._llm_url, json={"messages": messages,
                                                          "max_completion_tokens": self._llm_tokens,
                                                          "n": self._llm_responses,
                                                          "frequency_penalty": self._llm_frequency_p,
                                                          "presence_penalty": self._llm_presence_p,
                                                          "temperature": self._llm_temperature,
                                                          "verbosity": self._llm_verbosity})
            # Raise HTTPError for bad responses (4xx or 5xx)
            response.raise_for_status()
            result = response.json()
            content = []
            for reply in result['choices']:
                content.append(reply['message']['content'])
            wx.CallAfter(self._parent.llm_response_callback, content, False)
        except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
            wx.CallAfter(self._parent.llm_response_callback, Strings.msg_llm_connection_ok.format('ERROR',
                                                                                                  str(e)), True)
