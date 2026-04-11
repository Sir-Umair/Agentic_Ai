from langchain_anthropic import ChatAnthropic
from langchain_core.messages import AnyMessage, AIMessage, HumanMessage
from langgraph.graph import MessagesState, StateGraph, START, END, add_messages
from typing import Annotated
import requests
import os
import sys
from dotenv import load_dotenv
from collections import Counter
import json
from pprint import pprint
import random

# Ensure terminal supports Unicode characters (crucial for Windows)
if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        # Fallback for older python versions if needed
        import codecs
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
        sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())

load_dotenv()

# Global registry to track users and their IDs during the script run
SESSION_REGISTRY = {}

# =========================
# INITIALIZATION
# =========================
llm = ChatAnthropic(
    model="claude-sonnet-4-6",
    anthropic_api_key=os.getenv("ANTHROPIC_API_KEY")
)

# =========================
# STATE
# =========================
class State(MessagesState):
    github_username: str
    user_info: dict
    repos: list
    followers: list
    languages: dict
    yearly_activity: dict
    pull_requests: int
    follower_cohorts: dict
    error_message: str
    messages: Annotated[list[AnyMessage], add_messages]

# =========================
# NODES
# =========================

def login_node(state: State) -> dict:
    """
    Ensures the user is logged in via username and tracks session.
    """
    username = state.get("github_username")
    if username:
        SESSION_REGISTRY[username] = True
    return {"github_username": username}

def fetch_github_data(state: State) -> dict:
    """
    Fetches Profile, Repo, Follower, and Pull Request data.
    """
    userName = state.get("github_username")
    
    # Skip if data already fetched
    if state.get("user_info") and state.get("user_info").get("login") == userName:
        return {}
    
    # Helper to check for API errors
    def check_error(response):
        if isinstance(response, dict) and "message" in response:
            return response["message"]
        return None

    try:
        # Support optional GitHub Token
        headers = {}
        gh_token = os.getenv("GITHUB_TOKEN")
        if gh_token:
            headers["Authorization"] = f"token {gh_token}"

        # Helper to diagnostic rate limits
        def get_rate_info(resp):
            rem = resp.headers.get("X-RateLimit-Remaining", "?")
            reset = resp.headers.get("X-RateLimit-Reset", "")
            return rem, reset

        # 1. Fetch User Info
        resp = requests.get(f"https://api.github.com/users/{userName}", headers=headers, timeout=10)
        user_resp = resp.json()
        rem, _ = get_rate_info(resp)
        
        error = check_error(user_resp)
        if error or resp.status_code != 200:
            return {"error_message": f"GitHub API Error: {error or resp.status_code} (Quota: {rem} left)"}
        
        # 2. Fetch Repositories
        resp = requests.get(f"https://api.github.com/users/{userName}/repos", headers=headers, timeout=10)
        repos_resp = resp.json()
        if not isinstance(repos_resp, list): repos_resp = []
        
        # 3. Fetch Followers
        resp = requests.get(f"https://api.github.com/users/{userName}/followers", headers=headers, timeout=10)
        followers_resp = resp.json()
        if not isinstance(followers_resp, list): followers_resp = []

        # 4. Fetch Pull Requests (via Search API)
        print(" " * 4 + "→ Fetching Pull Request activity...")
        resp = requests.get(f"https://api.github.com/search/issues?q=author:{userName}+type:pr", headers=headers, timeout=10)
        pr_resp = resp.json()
        pr_count = pr_resp.get("total_count", 0) if isinstance(pr_resp, dict) else 0

        # 5. Fetch Follower Cohorts
        follower_years = []
        fetch_limit = 30 if gh_token else 10
        fol_to_fetch = followers_resp[:fetch_limit]
        total_fol = len(fol_to_fetch)
        
        if total_fol > 0:
            print(" " * 4 + f"→ Analyzing follower vintage ({total_fol} profiles)...")
            
        for f in fol_to_fetch:
            if isinstance(f, dict) and f.get('url'):
                try:
                    f_resp = requests.get(f['url'], headers=headers, timeout=10)
                    if f_resp.status_code == 200:
                        f_detail = f_resp.json()
                        if f_detail.get('created_at'):
                            follower_years.append(f_detail['created_at'][:4])
                    elif f_resp.status_code == 403:
                        print(" " * 4 + "! Rate limit reached during vintage analysis.")
                        break
                except:
                    continue
        cohort_counts = dict(Counter(follower_years))

        # --- DATA PROCESSING ---
        language_counts = dict(Counter([r['language'] for r in repos_resp if isinstance(r, dict) and r.get('language')]))
        yearly_counts = dict(Counter([r['created_at'][:4] for r in repos_resp if isinstance(r, dict) and r.get('created_at')]))

        return {
            "user_info": user_resp,
            "repos": repos_resp,
            "followers": followers_resp,
            "languages": language_counts,
            "yearly_activity": yearly_counts,
            "pull_requests": pr_count,
            "follower_cohorts": cohort_counts,
            "error_message": ""
        }
    except Exception as e:
        return {"error_message": f"Connection error: {str(e)}"}

def generative_respond(state: State) -> dict:
    """
    Analyzes query and responds naturally with standard terminal text.
    """
    if not state.get("messages"):
        return {"messages": []}
    query = state["messages"][-1].content
    user = state.get("user_info", {})
    repos = state.get("repos", [])
    followers = state.get("followers", [])
    languages = state.get("languages", {})
    yearly = state.get("yearly_activity", {})
    error_msg = state.get("error_message", "")

    # Provide context to Claude
    context = {
        "user": user.get("login", "Unknown") if user else "Unknown",
        "error": error_msg,
        "repo_count": len(repos),
        "follower_count": len(followers),
        "pull_requests": state.get("pull_requests", 0),
        "follower_cohorts": state.get("follower_cohorts", {}),
        "language_breakdown": languages,
        "yearly_activity": yearly,
        "repo_urls": [r['html_url'] for r in repos[:10]],
        "follower_urls": [f['html_url'] for f in followers[:10]]
    }

    prompt = f"""
    You are a specialized GitHub Agent for user '{context['user']}'.
    
    DATA CONTEXT: {json.dumps(context)}
    
    USER QUERY: "{query}"
    
    STRICT RULES:
    1. If the 'error' field in context is not empty, explain that the GitHub data is currently unavailable due to public limits.
    2. Answer ONLY questions related to the GitHub data provided.
    3. IF THE USER ASKS FOR A FOLLOWERS GRAPH OR GENERAL INFO:
       - Show 'Total Followers' count clearly.
       - Generate a HORIZONTAL ASCII bar chart of 'follower_cohorts'.
       - Use simple characters like '=' or '█' for bars.
    4. IF THE USER ASKS FOR SPECIFIC FOLLOWER DETAILS (names, URLs):
       - List the names or URLs as requested. Use the data in 'follower_urls' if available.
    5. IF THE USER ASKS FOR PERFORMANCE/ACTIVITY:
       - Show the relevant graph.
       - INCLUDE A PROFESSIONAL SUMMARY: Analyze growth and project trends.
    6. NO EMOJIS, STARS (*), or HASHES (#).
    7. Maintain a professional, direct, and insightful tone.
    """

    response_content = llm.invoke(prompt).content.strip()
    
    # Use the raw content now that terminal supports UTF-8
    clean_content = response_content.strip()
    
    # Professional ASCII Formatting 
    def draw_box(title, content_lines, width=70):
        top = "┌" + "─" * (width - 2) + "┐"
        bottom = "└" + "─" * (width - 2) + "┘"
        header = f"│ {title.center(width - 4)} │"
        sep = "├" + "─" * (width - 2) + "┤"
        output = [top, header, sep]
        for line in content_lines:
            line = line.strip()
            # Handle long lines by wrapping or truncating
            while len(line) > (width - 4):
                output.append(f"│ {line[:width - 4]} │")
                line = line[width - 4:]
            padded_line = f"│ {line.ljust(width - 4)} │"
            output.append(padded_line)
        output.append(bottom)
        return "\n".join(output)

    # Detect query focus
    asked_followers = any(x in query.lower() for x in ["follower"])
    is_graph_query = any(x in query.lower() for x in ["graph", "chart", "performance", "activity", "trend"])

    if is_graph_query or asked_followers:
        title = "FOLLOWER PERFORMANCE" if asked_followers else "GITHUB ACTIVITY"
        box = draw_box(title, clean_content.split("\n"))
        print("\n" + box)
    else:
        print("\n" + clean_content)
    
    return {"messages": [AIMessage(content=response_content)]}

def privacy_cleanup(state: State) -> dict:
    """
    Clears the username from registry and state.
    """
    username = state.get("github_username")
    if username in SESSION_REGISTRY:
        del SESSION_REGISTRY[username]
    print(f"\n[PRIVACY] Information for '{username}' has been purged from memory.")
    return {
        "github_username": "",
        "user_info": {},
        "repos": [],
        "followers": [],
        "languages": {},
        "yearly_activity": {},
        "pull_requests": 0
    }

# =========================
# BUILD GRAPH
# =========================
builder = StateGraph(State)

builder.add_node("login_node", login_node)
builder.add_node("fetch_github_data", fetch_github_data)
builder.add_node("generative_respond", generative_respond)
builder.add_node("privacy_cleanup", privacy_cleanup)

builder.add_edge(START, "login_node")
builder.add_edge("login_node", "fetch_github_data")
builder.add_edge("fetch_github_data", "generative_respond")
builder.add_edge("generative_respond", END)

graph = builder.compile()

# =========================
# RUN
# =========================
if __name__ == "__main__":
    print("-" * 50)
    print(" GITHUB PERSONAL DATA AGENT (Username-Only)")
    print("-" * 50)
    
    while True:
        target_name = input("\n[LOGIN] Enter GitHub Username (or 'exit'): ").strip()
        if target_name.lower() == 'exit': break
        if not target_name: continue
        
        # Initial State for the session
        state = {
            "github_username": target_name,
            "messages": [],
            "user_info": {},
            "repos": [],
            "followers": [],
            "languages": {},
            "yearly_activity": {},
            "pull_requests": 0,
            "follower_cohorts": {},
            "error_message": ""
        }
        
        # Run graph once to fetch data
        print(f"[SYSTEM] Fetching data for {target_name}...")
        state = graph.invoke(state)
        
        current_session_active = True
        while current_session_active:
            if state.get("error_message"):
                print(f"[ERROR] {state['error_message']}")
                break

            query = input(f"\n[QUERY] What would you like to know about {target_name}? ").strip()
            if query.lower() in ['exit', 'logout', 'quit']:
                break
            
            # Update state with new user message
            state["messages"].append(HumanMessage(content=query))
            state = graph.invoke(state)
            
            # Privacy and Session Menu
            print("\n" + "─" * 40)
            choice = input("[MENU] (c)ontinue, (p)urge & logout, (l)ogout only: ").strip().lower()
            if choice == 'p':
                state = privacy_cleanup(state)
                current_session_active = False
            elif choice == 'l':
                current_session_active = False
            # 'c' or anything else continues the loop
    
    print("\n[SYSTEM] Application shutdown.")
    print("-" * 50)