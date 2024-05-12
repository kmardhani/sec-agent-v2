from typing import Callable, Dict, List, Literal, Any, Optional, Union
from autogen import ConversableAgent
from autogen.agentchat.agent import Agent
from .sec_downloader_assistant import SecDownloaderAssistant
from .sec_rag_assistant import SecRagAssistant


class SecAgent(ConversableAgent):
    _dl_assistant = None
    _rag_assistant = None

    DEFAULT_REPLY = "TERMINATE"

    def __init__(self, name: str, 
                 human_input_mode: Optional[str] = "NEVER",  # Fully automated
                 default_auto_reply: Optional[Union[str, Dict, None]] = DEFAULT_REPLY,
                 **kwargs: Any):
        super().__init__(
            name=name, 
            human_input_mode=human_input_mode,
            default_auto_reply=default_auto_reply,
            **kwargs)

        self._dl_assistant = SecDownloaderAssistant()
        self._rag_assistant = SecRagAssistant()

        self.register_reply([Agent, None], SecAgent._generate_sec_reply, position=2)
    
    def _generate_sec_reply(
        self,
        messages: Optional[List[Dict]] = None,
        sender: Optional[Agent] = None,
        config: Optional[Any] = None,
    ):
        prompt = messages[-1]["content"]

        if prompt == "":
            return True, self._default_auto_reply
        
        print(f"Promt = {prompt}")

        file_list = self._dl_assistant.download_sec_filings(prompt=prompt)
        print(f"Files downloded: {file_list}")

        if len(file_list) > 0:
            response = self._rag_assistant.ask_question(
                file_list=file_list, question=prompt
            )
        else:
            response = "Unable to answer this question."
    
        return True, response
