# Agentic Microservices Pattern: LangGraph + CrewAI + FastMCP

A production-grade architecture pattern demonstrating the separation of **Workflow Orchestration (LangGraph)**, **Multi-Agent Reasoning (CrewAI)**, and **Standardized Tool Integration (MCP Server)** using **OpenRouter** and **`uv`**.

---
### 📁 Repository Structure
⚬	mcp-server/: FastMCP HTTP SSE server exposing a GitHub inspection tool.
⚬	mcp-crew/: Core CrewAI multi-agent definition (McpCrew) exposed as a reusable package.
⚬	langgraph-orchestrator/: LangGraph state machine invoking the McpCrew module.

---

## 🏗 Architecture Overview

```text
[ LangGraph Orchestrator ]
         │
         │ (State Control & Execution Node)
         ▼
[ CrewAI Multi-Agent System ]
         │
         │ (HTTP / SSE Protocol via MCPServerAdapter)
         ▼
[ FastMCP Tool Server ] ──► (HTTP Request) ──► External APIs (GitHub API)
```
---
### 🔄 Execution Flow
	1.	LangGraph initializes state (username = 'torvalds') and invokes the call_crew node.
	2.	CrewAI initializes the github_auditor agent, passing parameters down to the task.
	3.	CrewAI Agent calls the MCP Tool over HTTP SSE to fetch live GitHub metrics.
	4.	MCP Server processes the request via GitHub API and streams structured output back to CrewAI.
	5.	CrewAI generates a final audit report and returns the result back to LangGraph.

### Why This Pattern?
⚬	LangGraph (Control Plane): Manages deterministic workflows, state transitions, and execution boundaries.
⚬	CrewAI (Reasoning Layer): Handles non-deterministic, agent-to-agent collaboration and context synthesis.
⚬	FastMCP (Tool Protocol): Standardizes tool definitions over HTTP/SSE, decoupling API integration from agent logic.

### 🛠 Prerequisites
⚬	Python 3.10+
⚬	uv Package Manager: Install via curl -LsSf https://astral.sh/uv/install.sh | sh
⚬	OpenRouter API Key: Set as environment variable (OPENAI_API_KEY)