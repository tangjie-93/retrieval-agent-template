"""Let ChatGPT choose and call a local LangChain tool."""

from langchain.agents import create_agent
from langchain_core.tools import tool

from common import get_chat_model


@tool
def search_policy(query: str) -> str:
    """Search enterprise policy snippets. Use this for leave or reimbursement rules."""
    if "年假" in query:
        return "员工工作满一年后，每年享有 5 天年假。"
    if "报销" in query:
        return "单笔超过 5000 元的报销，需要部门负责人审批。"
    return "No matching policy was found."


agent = create_agent(
    model=get_chat_model(),
    tools=[search_policy],
    system_prompt="Answer policy questions in Chinese. Use search_policy before answering.",
)
result = agent.invoke({
    "messages": [{"role": "user", "content": "工作满一年有几天年假？"}]
})
print(result["messages"][-1].content)
