import os
import streamlit as st
import pandas as pd
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from mcp_crew.crew import McpCrew

# Load environment variables
load_dotenv()

# Define LangGraph workflow node
def call_crew(state):
    crew_result = McpCrew().crew().kickoff(inputs={'username': state['username']})
    return {'result': crew_result}

# Build LangGraph State Workflow
@st.cache_resource
def get_workflow():
    builder = StateGraph(dict)
    builder.add_node("call_crew", call_crew)
    builder.add_edge(START, "call_crew")
    builder.add_edge("call_crew", END)
    return builder.compile()

# Page configuration
st.set_page_config(page_title="GitHub Auditor AI", page_icon="🔍", layout="wide")
st.title("🔍 GitHub Security Auditor & Activity Pipeline")
st.caption("Powered by LangGraph, CrewAI, and Model Context Protocol (MCP)")

# Search Input Form
with st.form("github_search_form"):
    username_input = st.text_input("Enter GitHub Username:", value="sathyalog", placeholder="e.g. octocat")
    submit_button = st.form_submit_button("Run Audit", type="primary")

if submit_button:
    if not username_input.strip():
        st.warning("Please enter a valid GitHub username.")
    else:
        with st.spinner(f"Executing MCP Crew audit for '{username_input}'..."):
            try:
                workflow = get_workflow()
                response = workflow.invoke({'username': username_input.strip()})
                
                # Extract output from LangGraph state
                raw_result = response.get('result')
                output_text = str(raw_result.raw if hasattr(raw_result, 'raw') else raw_result)
                
                st.success("Audit complete!")
                
                # Render tabular summary
                st.subheader("📋 Developer Activity Summary")
                
                data = {
                    "Metric / Field": ["Target Username", "Audit Status", "Raw Crew Output Summary"],
                    "Details": [username_input, "Completed Successfully", output_text]
                }
                
                df = pd.DataFrame(data)
                st.table(df)
                
                # Full report viewer
                with st.expander("View Full Unformatted Audit Log"):
                    st.text(output_text)
                    
            except Exception as e:
                st.error(f"Execution failed: {str(e)}")
