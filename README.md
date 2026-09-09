# Agentic Microservices Pattern: LangGraph + CrewAI + FastMCP

A production-grade architecture pattern demonstrating the separation of **Workflow Orchestration (LangGraph)**, **Multi-Agent Reasoning (CrewAI)**, and **Standardized Tool Integration (MCP Server)** using **OpenRouter** and **`uv`**.

### 🏗️ Architecture & Pattern Overview

This pipeline uses an Orchestrator-Agent-Tool design pattern. LangGraph acts as the state manager, CrewAI handles agent logic, and the MCP server exposes standardized tools for system data access.

📂 Complete Project Folder Structure

agentic-mcp-pipeline/                      # Workspace root directory
│
├── mcp-server/                             # REPO 1: FastMCP Server Project
│   ├── main.py                             # Runs FastAPI/FastMCP server on port 8000
│   ├── pyproject.toml                      # FastMCP dependencies configuration
│   └── README.md                           # Documentation for server setup
│
├── mcp-crew/                               # REPO 2: Standalone CrewAI Package
│   ├── pyproject.toml                      # Package config defining mcp-crew build rules
│   ├── README.md                           # Documentation for crew package
│   └── mcp_crew/                          # Core Python package module
│       ├── __init__.py                     # Package initialization file
│       ├── crew.py                         # Defines McpCrew class, Agent, Task, & MCP adapter
│       └── config/                         # Optional YAML configuration directory
│           ├── agents.yaml                 # Agent roles and goals configuration
│           └── tasks.yaml                  # Task descriptions and expected outputs
│
└── langgraph-orchestrator/                # REPO 3: LangGraph & Streamlit Orchestrator
    ├── main.py                             # Streamlit UI & LangGraph state execution pipeline
    ├── pyproject.toml                      # References local "../mcp-crew" dependency
    ├── .env                                # API keys (OPENAI_API_KEY, OPENROUTER_API_KEY)
    └── README.md                           # Main user and execution guide


### 🛠️ Repository Breakdown & Inter-Package Connections

1. mcp-server (Repo 1: The API Provider)

⚬ Tech Stack: Python, FastMCP, GitHub REST API, Uvicorn
⚬ What it does: Runs as an independent local HTTP service on `http://localhost:8000/sse`. It wraps external GitHub API calls and exposes them as standard MCP tools over Server-Sent Events (SSE).

2. mcp-crew (Repo 2: The Logic Package)

⚬ Tech Stack: Python, CrewAI, crewai-tools (MCPServerAdapter), OpenRouter / LiteLLM
⚬ Why it has crew.py: crew.py defines the core McpCrew class. It initializes the github_auditor agent, configures the MCPServerAdapter to discover tools from Repo 1, sets up the LLM parameters, and defines the execution task (audit_task).

3. langgraph-orchestrator (Repo 3: The Orchestrator & UI)

⚬ Tech Stack: Python, LangGraph, Streamlit, uv
⚬ How it connects: It installs mcp-crew as a local editable package using uv add ../mcp-crew. This imports McpCrew directly into its LangGraph execution nodes and displays results through a Streamlit UI.

### 🔌 How mcp-server Works as an API

⚬ Acts as a tool provider that decouples external API logic from the LLM framework.
⚬ Exposes standard SSE endpoints (http://localhost:8000/sse) so any agent framework can auto-discover available tools.
⚬ Wraps GitHub REST endpoints directly, enforcing structured parameters and security protocols.

### 🤖 CrewAI Agent & Task Breakdown

The Agent: GitHub Security Auditor

⚬ Connects via MCPServerAdapter to read available tools from the local SSE stream.
⚬ Uses gpt-4o-mini (via OpenRouter) to decide when and how to invoke MCP tools dynamically.

The Task: Developer Activity Audit

⚬ Accepts {username} as dynamic context input from the runtime state.
⚬ Fetches profile metrics and top public repositories to synthesize a clean activity summary.

### 🔄 Invoking CrewAI Inside LangGraph

# Executed inside a LangGraph State Node
```def call_crew(state):
    crew_result = McpCrew().crew().kickoff(inputs={'username': state['username']})
    return {'result': crew_result}
```

⚬ LangGraph encapsulates `McpCrew().crew().kickoff()` inside an execution node.
⚬ Inputs pass seamlessly from the Streamlit UI into the LangGraph state context dictionary.
⚬ Ensures state persistent logging and exception handling surrounding agent execution.

### 🎯 Why We Chose This Approach

⚬ Decoupled Architecture: Separates interface logic, agent reasoning, and data sources into independent components.
⚬ Standardized Tooling: MCP allows swapping tool endpoints without altering agent or UI codebase logic.
⚬ Stateful Execution: LangGraph manages multi-step execution flows, retries, and UI state tracking reliably.

⚡ Real-Time Benefits

⚬ Tool Reusability: The MCP server can be reused across different agent frameworks or LLM models instantly.
⚬ Modular Scalability: Scale or replace individual servers without touching orchestrator pipelines.
⚬ Streamlined Debugging: Isolate agent reasoning bugs from data retrieval errors with clear boundary lines.

### ⚙️ How We Connected the 3 Repositories

1. Repo 1 (mcp-server) starts and listens on `http://localhost:8000/sse`.
2. Repo 2 (mcp-crew) connects to Repo 1 via MCPServerAdapter(url="http://localhost:8000/sse") inside crew.py.
3. Repo 3 (langgraph-orchestrator) installs Repo 2 as a local Python package dependency:
   ```cd langgraph-orchestrator
   uv add ../mcp-crew```
   
4. Repo 3 imports McpCrew directly from mcp_crew.crew to execute state updates.

### 🚀 Setup & Execution Guide

Prerequisites

⚬ Python 3.12+
⚬ uv package manager installed

Step 1: Configure Environment Variables

Create a .env file inside langgraph-orchestrator/:
```
OPENAI_API_KEY=sk-or-v1-your-key-here
OPENROUTER_API_KEY=sk-or-v1-your-key-here
OPENAI_API_BASE=https://openrouter.ai/api/v1
MODEL=gpt-4o-mini
```

Step 2: Start mcp-server (Terminal 1)
```
cd mcp-server
uv run main.py
```

Starts the FastMCP server on `http://localhost:8000/sse`.

Step 3: Launch Streamlit App (Terminal 2)
```
cd langgraph-orchestrator
uv run streamlit run main.py
```

Opens the web interface in your browser.

### ❓ Why Must Both Services Run Simultaneously?

⚬ mcp-server acts as the live backend hosting external API tools over local SSE connections.
⚬ langgraph-orchestrator acts as the frontend runtime that calls mcp-server endpoints dynamically.
⚬ If mcp-server stops running, CrewAI agents lose tool access and cannot fetch live data.

### 🔧 Reinstalling Package & Troubleshooting

How to Reinstall the mcp-crew Package

If you make code changes inside mcp-crew/mcp_crew/crew.py, re-sync the dependency in Repo 3 so changes reflect immediately:
```
cd langgraph-orchestrator
uv sync --reinstall-package mcp-crew
```

Common Issues & Quick Fixes

⚬ ValueError: API Key is missing
  ⚬ Fix: Ensure load_dotenv() is loaded in main.py or export keys directly in terminal:
    export OPENAI_API_KEY="sk-or-v1-xxx"
    export OPENROUTER_API_KEY="sk-or-v1-xxx"
    
⚬ Connection Refused on http://localhost:8000/sse
  ⚬ Fix: mcp-server is not running. Open Terminal 1, navigate to mcp-server, and run uv run main.py.
⚬ ModuleNotFoundError: No module named 'mcp_crew'
  ⚬ Fix: Run uv add ../mcp-crew from inside the langgraph-orchestrator folder.

### ✨ Key Advantages of This Pattern

⚬ Enterprise Modularity: Microservice structure allows separate teams to manage tools and agent logic.
⚬ Vendor Agnostic: Easily swap model providers via OpenRouter without modifying data pipelines.
⚬ Interactive UI: Streamlit gives end users immediate control over complex autonomous workflows.

### Screenshots:
![screen1](<Screenshot 2026-09-09 at 4.18.00 PM.png>) 
![screen2](<Screenshot 2026-09-09 at 4.18.13 PM.png>)