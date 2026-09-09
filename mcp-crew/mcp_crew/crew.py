import os
from pathlib import Path
from dotenv import load_dotenv
from crewai import Agent, Crew, Task, Process, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import MCPServerAdapter

# Resolve root workspace directory explicitly
CURRENT_DIR = Path(__file__).resolve().parent
WORKSPACE_ROOT = CURRENT_DIR.parents[1]  # points to agentic-mcp-pipeline

# Try loading from local, package root, or top-level project root
load_dotenv(CURRENT_DIR / ".env")
load_dotenv(WORKSPACE_ROOT / "langgraph-orchestrator" / ".env")
load_dotenv(WORKSPACE_ROOT / "mcp-crew" / ".env")
load_dotenv(WORKSPACE_ROOT / ".env")

@CrewBase
class McpCrew:
    """McpCrew for GitHub Auditing via MCP"""

    def __init__(self):
        # Fetch key from environment
        api_key = os.getenv("OPENAI_API_KEY") or os.getenv("OPENROUTER_API_KEY")
        base_url = os.getenv("OPENAI_API_BASE", "https://openrouter.ai/api/v1")
        model_name = os.getenv("MODEL", "gpt-4o-mini")

        if not api_key:
            raise ValueError(
                f"API Key is missing! Checked environment variables.\n"
                f"Current Working Dir: {os.getcwd()}\n"
                f"Ensure OPENAI_API_KEY or OPENROUTER_API_KEY is present in your .env file."
            )

        # LiteLLM/CrewAI needs these populated in os.environ for OpenRouter routing
        os.environ["OPENROUTER_API_KEY"] = api_key
        os.environ["OPENAI_API_KEY"] = api_key

        self.llm = LLM(
            model=f"openrouter/{model_name}",
            api_key=api_key,
            base_url=base_url
        )

    @agent
    def github_auditor(self) -> Agent:
        server_params = {"url": "http://localhost:8000/sse"}
        adapter = MCPServerAdapter(server_params)
        mcp_tools = adapter.tools if hasattr(adapter, 'tools') else [adapter]

        return Agent(
            role="GitHub Security Auditor",
            goal="Analyze profile details and top public repositories for user '{username}'.",
            backstory="You are an automated code auditing agent retrieving profile information over MCP.",
            tools=mcp_tools,
            llm=self.llm,
            verbose=True
        )

    @task
    def audit_task(self) -> Task:
        return Task(
            description=(
                "Fetch profile data and top public repos for GitHub user '{username}' using the MCP tool. "
                "Synthesize the data into a high-level developer activity summary."
            ),
            expected_output="A clean, structured summary report of the GitHub user.",
            agent=self.github_auditor()
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )
