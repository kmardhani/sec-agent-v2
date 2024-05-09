from sec_agent_v2 import sec_agent
from autogen import UserProxyAgent

def termination_msg(x):
        return isinstance(x, dict) and "TERMINATE" == str(x.get("content", ""))[-9:].upper()

prompt = "Conduct a thorough analysis of 3M's  market performance for 2022. This includes examining key financial metrics such as P/E ratio, EPS growth, revenue trends, and debt-to-equity ratio."

sec = sec_agent.SecAgent(name="SEC Agent", is_termination_msg=termination_msg)

user = UserProxyAgent("Financial Analyst", is_termination_msg=termination_msg)

cr = user.initiate_chat(sec, message=prompt)