from typing import Callable, Dict, List, Literal, Any, Optional, Union
from autogen import ConversableAgent
from autogen.agentchat.agent import Agent
from .sec_downloader_assistant import SecDownloaderAssistant
from .sec_rag_assistant import SecRagAssistant


class SecAgent(ConversableAgent):
    _dl_assistant = None
    _rag_assistant = None

    def __init__(self, name: str, **kwargs: Any):
        super().__init__(name, **kwargs)

        self._dl_assistant = SecDownloaderAssistant()
        self._rag_assistant = SecRagAssistant()

    def generate_reply(
        self,
        messages: Optional[List[Dict[str, Any]]] = None,
        sender: Optional["Agent"] = None,
        **kwargs: Any,
    ) -> Union[str, Dict, None]:

        prompt = messages[-1]["content"]
        print(f"Promt = {prompt}")

        file_list = self._dl_assistant.download_sec_filings(prompt=prompt)
        print(f"Files downloded: {file_list}")

        if len(file_list) > 0:
            response = self._rag_assistant.ask_question(
                file_list=file_list, question=prompt
            )
        else:
            response = "Unable to answer this question."

        return {"role": "assistant", "content": response}
