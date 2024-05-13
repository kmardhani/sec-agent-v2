from dotenv import load_dotenv
import os
import json
from typing import List, Union, Optional, Dict, Tuple
from openai import OpenAI
from .get_sec_filing import (
    get_sec_filing,
    get_sec_filing_description,
    param_ticker_description,
    param_report_type_description,
    param_period_of_report_description,
)

"""
Assitant based on openai's assistant API that uses LLM to figure out
which SEC files to download and stores these SEC files to the folder
specified in WORK_DIR env. variable,
"""


class SecDownloaderAssistant:

    _download_assistant = None
    _client = None
    _working_dir = None

    def __init__(self) -> None:

        load_dotenv()
        self._working_dir = os.getenv("WORK_DIR")

        self._client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self._download_assistant = self._client.beta.assistants.create(
            instructions="You are a financial analyst. Use the provided functions to answer questions.",
            model="gpt-4-turbo",
            tools=[
                {
                    "type": "function",
                    "function": {
                        "name": "get_sec_filing",
                        "description": get_sec_filing_description,
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "ticker": {
                                    "type": "string",
                                    "description": param_ticker_description,
                                },
                                "report_type": {
                                    "type": "string",
                                    "description": param_report_type_description,
                                },
                                "period_of_report": {
                                    "type": "string",
                                    "description": param_period_of_report_description,
                                },
                            },
                            "required": [
                                "ticker",
                                "report_type",
                                "period_of_report",
                                "download_dir",
                            ],
                        },
                    },
                },
            ],
        )

    def download_sec_filings(self, messages: Optional[List[Dict]] = None) -> Tuple[List[str], str]:

        file_list = []
        msg = ""

        # messages list must not be None
        if messages is None:
            msg = "Internal Error:  Messages can not be None"
            return file_list, msg
        
        # message list can not contain empty content
        for message in messages:
            if message['content'] == '':
                 messages.remove(message)

        # messages list must have atleast 1 message
        if len(messages) < 1:
            msg = "Internal Error: Messages list can not be empty"

        thread = self._client.beta.threads.create(
            messages=messages
        )

        run = self._client.beta.threads.runs.create_and_poll(
            thread_id=thread.id, assistant_id=self._download_assistant.id
        )

        if run.status == "requires_action":
            for tool in run.required_action.submit_tool_outputs.tool_calls:
                if tool.function.name == "get_sec_filing":
                    arg_list = json.loads(tool.function.arguments)
                    ticker = arg_list["ticker"]
                    report_type = arg_list["report_type"]
                    period_of_report = arg_list["period_of_report"]
                    print(
                        f"Calling function get_sec_filing with args: {ticker} {report_type} {period_of_report}"
                    )
                    file_list += get_sec_filing(
                        ticker=ticker,
                        report_type=report_type,
                        period_of_report=period_of_report,
                    )
                    if len(file_list) > 0:
                        msg = f"Downloaded {len(file_list)} files"
                    else:
                        msg = "No matching file(s) found for this criteria"
        elif run.status == "completed":
            messages = list(self._client.beta.threads.messages.list(thread_id=thread.id, run_id=run.id))
            if len(messages) > 0:
                if len(messages[0].content) > 0:
                    msg = messages[0].content[0].text.value
        else:
            msg = f"Error status: {run.status}"
        return file_list, msg
