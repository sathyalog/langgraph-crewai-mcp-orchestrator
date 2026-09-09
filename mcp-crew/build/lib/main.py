import os
from crewai import Agent, Crew, Task, Process
from crewai_tools import MCPServerAdapter
from langchain_openai import ChatOpenAI

def run_github_crew(username: str) -> str:
    os.environ["OPENAI_API_BASE"] = "https://openrouter.ai/api/v1"
    os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "sk-or-v1-xxxxxx")
    
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        openai_api_base="https://openrouter.ai/api/v1",
        openai_api_key=os.environ["OPENAI_API_KEY"]
    )

    server_params = {"url": "http://localhost:8000/sse"}
    
    with MCPServerAdapter(server_params) as mcp_tools:
        auditor_agent = Agent(
            role="GitHub Security & Activity Auditor",
            goal=f"Analyze activity and structure of GitHub user '{username}'.",
            backstory="You are an expert developer auditing user accounts via MCP tools.",
            tools=mcp_tools,
            llm=llm,
            verbose=True
        )

        audit_task = Task(
            description=(
                f"1. Fetch data for GitHub user '{username}' using the MCP tool.\n"
                f"2. Summarize their public activity, repo count, and list recent projects."
            ),
            expected_output="A structured summary report of the GitHub user.",
            agent=auditor_agent
        )

        crew = Crew(
            agents=[auditor_agent],
            tasks=[audit_task],
            process=Process.sequential
        )

        return str(crew.kickoff())