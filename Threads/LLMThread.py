import json
from threading import Thread

import requests
import wx

from Constants import Strings


class LLMThread(Thread):
    """
    Thread for talking to LLM.
    """

    def __init__(self, parent, prompt: str, system_prompt: str, llm_url: str) -> None:
        """
        Thread constructor.
        :param parent: The Frame that called the thread.
        :param prompt: Prompt.
        :param system_prompt: System prompt.
        :param llm_url: LLM REST api point compatible with open AI.
        :return: None
        """
        super().__init__()
        self._parent = parent
        self._prompt = prompt
        self._system_prompt = system_prompt
        self._llm_url = llm_url
        self.start()

    def run(self) -> None:
        """
        Send a prompt to LLM on url and get a string response.
        :return: None
        """
        # todo limit tokens and other settings, heat and so on...
        # This does not retain context, that would have to be passed along inside messages.
        messages = [{"role": "system", "content": self._system_prompt},
                    {"role": "user", "content": self._prompt}]
        try:
            response = requests.post(self._llm_url, json={"messages": messages})
            # Raise HTTPError for bad responses (4xx or 5xx)
            response.raise_for_status()
            result = response.json()
            content = result['choices'][0]['message']['content']
            wx.CallAfter(self._parent.llm_response_callback, content, False)
        except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
            wx.CallAfter(self._parent.llm_response_callback, Strings.msg_llm_connection_ok.format('ERROR',
                                                                                                  str(e)), True)
