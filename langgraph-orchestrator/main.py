import os
from dotenv import load_dotenv

# Load environment variables from langgraph-orchestrator/.env
load_dotenv()

from langgraph.graph import StateGraph, START, END
from mcp_crew.crew import McpCrew

def call_crew(state):
    crew_result = McpCrew().crew().kickoff(inputs={'username': state['username']})
    return {'result': crew_result}

# Set up LangGraph State Workflow
builder = StateGraph(dict)
builder.add_node("call_crew", call_crew)
builder.add_edge(START, "call_crew")
builder.add_edge("call_crew", END)

workflow = builder.compile()

if __name__ == "__main__":
    result = workflow.invoke({'username': 'sathyalog'})
    print(result)
