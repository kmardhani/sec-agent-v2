from openai import OpenAI
import os
from dotenv import load_dotenv
from typing import List, Optional, Dict

"""
openai based assistant that uses openai's RAG pipeline to answer SEC
filing related questions.  Assumes SEC filings are already downloaded.
"""


class SecRagAssistant:

    _rag_assistant = None
    _client = None

    def __init__(self) -> None:

        load_dotenv()

        self._client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        self._rag_assistant = self._client.beta.assistants.create(
            name="SEC Filing Analyst",
            instructions="You are an expert financial analyst. Use you knowledge base to answer questions about audited financial statements.",
            model="gpt-4-turbo",
            tools=[{"type": "file_search"}],
        )

    def ask_question(self, file_list: List[str], messages: Optional[List[Dict]] = None,) -> str:

        vector_store = self._client.beta.vector_stores.create(
            name="Financial Statements"
        )
        file_streams = [open(path, "rb") for path in file_list]

        # upload files
        file_batch = self._client.beta.vector_stores.file_batches.upload_and_poll(
            vector_store_id=vector_store.id, files=file_streams
        )
        print(file_batch.status)
        print(file_batch.file_counts)

        self._rag_assistant = self._client.beta.assistants.update(
            assistant_id=self._rag_assistant.id,
            tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
        )

        thread = self._client.beta.threads.create(
            messages=messages
        )

        run = self._client.beta.threads.runs.create_and_poll(
            thread_id=thread.id, assistant_id=self._rag_assistant.id
        )

        answer = ""

        messages = list(
            self._client.beta.threads.messages.list(thread_id=thread.id, run_id=run.id)
        )

        if len(messages) > 0:
            if len(messages[0].content) > 0:
                message_content = messages[0].content[0].text
                annotations = message_content.annotations
                citations = []
                for index, annotation in enumerate(annotations):
                    message_content.value = message_content.value.replace(
                        annotation.text, f"[{index}]"
                    )
                    if file_citation := getattr(annotation, "file_citation", None):
                        cited_file = self._client.files.retrieve(file_citation.file_id)
                        citations.append(f"[{index}] {cited_file.filename}")

                answer = message_content.value + "\n" + "\n".join(citations)

        return answer
