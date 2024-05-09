from sec_api import QueryApi
import os
import requests
from dotenv import load_dotenv
from typing import List

get_sec_filing_description = """
This function downloads the SEC filings in the pdf format and saves them
to the disk in the provided folder.
"""

param_ticker_description = """
ticker symbol for which the filings are to be downloaded
"""

param_report_type_description = """
SEC form type,  For example "10-K" or "10-Q"
"""

param_period_of_report_description = """
End date when the reporting period ends
"""


def get_sec_filing(
    ticker: str,
    report_type: str,
    period_of_report: str,
) -> List[str]:
    load_dotenv()

    metadata = _get_metadata_for_a_form(ticker, report_type, period_of_report)

    file_list = []

    if len(metadata) > 0:
        file_list = _download_pdf_filings(
            metadata=metadata,
        )
    else:
        print("SEC filing for this criteria not found.  Returning empty file list")

    return file_list


def _get_metadata_for_a_form(ticker: str, report_type: str, period_of_report: str):

    queryApi = QueryApi(api_key=os.getenv("SEC_API_KEY"))

    query_string = (
        f'{ticker} AND periodOfReport:{period_of_report} AND formType:"{report_type}"'
    )

    query = {
        "query": {
            "query_string": {"query": query_string, "time_zone": "America/New_York"}
        },
        "from": 0,
        "size": "200",
        "sort": [{"periodOfReport": {"order": "desc"}}],
    }

    response = queryApi.get_filings(query)

    filings = response["filings"]

    metadata = list(
        map(
            lambda f: {
                "ticker": f["ticker"],
                "cik": f["cik"],
                "formType": f["formType"],
                "filedAt": f["filedAt"],
                "filingUrl": f["linkToFilingDetails"],
            },
            filings,
        )
    )

    return metadata


def _download_pdf_filings(metadata: list) -> List[str]:

    API_ENDPOINT = "https://api.sec-api.io/filing-reader"

    file_list = []

    for data in metadata:
        ticker = data["ticker"]
        new_folder = f"{os.getenv("WORK_DIR")}/{ticker}"

        if not os.path.isdir(new_folder):
            os.makedirs(new_folder)

        filingUrl = data["filingUrl"]
        filingUrl = filingUrl.replace("ix?doc=/", "")

        api_url = (
            API_ENDPOINT
            + "?token="
            + os.getenv("SEC_API_KEY")
            + "&url="
            + filingUrl
            + "&type=pdf"
        )

        response = requests.get(api_url)
        file_name = filingUrl.split("/")[-1]
        file_name = file_name.split(".")[0] + ".pdf"

        with open(new_folder + "/" + file_name, "wb") as f:
            f.write(response.content)

        file_list.append(new_folder + "/" + file_name)

    return file_list


# for testing
if __name__ == "__main__":
    file_list = get_sec_filing(
        ticker="BBY", report_type="10-K", period_of_report="2019-02-02"
    )
    print(file_list)
