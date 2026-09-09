import httpx
from mcp.server.mcpserver import MCPServer

# Initialize MCPServer in MCP v2.x
mcp = MCPServer("GitHub User Inspector", description="Fetch GitHub user profile info and top public repositories.")

@mcp.tool()
def inspect_github_user(username: str = "sathyalog") -> str:
    """Fetch profile info and top public repositories for a given GitHub username."""
    headers = {"User-Agent": "MCP-Server-App"}
    
    with httpx.Client(headers=headers, follow_redirects=True) as client:
        user_res = client.get(f"https://api.github.com/users/{username}")
        if user_res.status_code != 200:
            return f"Error: Failed to fetch user '{username}'. Status: {user_res.status_code}"
        
        user_data = user_res.json()
        repos_res = client.get(f"https://api.github.com/users/{username}/repos?sort=updated&per_page=5")
        repos_data = repos_res.json() if repos_res.status_code == 200 else []

    repo_names = [r["name"] for r in repos_data]
    
    return (
        f"GitHub User: {user_data.get('login')}\n"
        f"Name: {user_data.get('name', 'N/A')}\n"
        f"Public Repos Count: {user_data.get('public_repos')}\n"
        f"Followers: {user_data.get('followers')}\n"
        f"Recent Repositories: {', '.join(repo_names)}\n"
    )

if __name__ == "__main__":
    mcp.run(transport="sse")
