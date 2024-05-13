from sec_agent_v2 import sec_agent
from autogen import UserProxyAgent

def termination_msg(x):
        return x.get("content", "") and x.get("content", "").rstrip().endswith("TERMINATE")

# prompt = "Conduct a thorough analysis of 3M's  market performance for 2022. This includes examining key financial metrics such as P/E ratio, EPS growth, revenue trends, and debt-to-equity ratio."
prompt = "When is christ birthday"

sec = sec_agent.SecAgent(name="SEC Agent", is_termination_msg=termination_msg, human_input_mode="NEVER")

desc = """
You are financial analyst.  Evaluate the responses you get for completeness.  Respond with "TERMINATE" if satisfied with the answer, otherwise provide
explanation why you are not satisfied.
"""

user = UserProxyAgent("Financial Analyst", is_termination_msg=termination_msg, human_input_mode="ALWAYS", system_message=desc, max_consecutive_auto_reply=1)

cr = user.initiate_chat(sec, message=prompt)