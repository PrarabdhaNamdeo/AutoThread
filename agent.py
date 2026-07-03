import os
import requests
from typing import TypedDict
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from tavily import TavilyClient
from langgraph.graph import StateGraph, END

load_dotenv()
tavily_client = TavilyClient()

class AgentState(TypedDict):
    """
    State of the Agent 
    """
    topic: str
    research: str
    draft: str
    approved: bool
    feedback: str

llm = ChatGroq(
    model="llama-3.3-70b-versatile"
)

def research(state: AgentState):
    """
    Research about the given topic.
    """
    topic = state['topic']
    response = tavily_client.search(topic)
    results = response["results"]

    research_text = " ".join([result["content"] for result in results])

    return {"research": research_text}

def generate_draft(state: AgentState):
    """
    Generate a draft based on the topic.
    """
    topic = state['topic']
    feedback = state.get('feedback')
    research = state.get('research')

    if feedback:
        prompt = f"""
        You are a Threads post writer. Rewrite the following draft about {topic}.
        User feedback: {feedback}
        Research context: {research}
        Rules:
            - No URLs or links
            - Under 500 characters
            - Return ONLY the rewritten post, no commentary, no "ok", no explanation.
            """
    else:
        prompt = f"Write a Threads post about {topic}. Use this research as context: {research}. Keep it under 500 characters, make it engaging. Do not include any URLs, links, or placeholder links like [link]."

    response = llm.invoke(prompt).content

    return {"draft": response}

def human_review(state: AgentState):
    """
    Take human feedback on the draft.
    """
    draft = state["draft"]
    print(draft)

    user_input = input("Enter your feedback on the draft (approve/reject/edit): ")

    if user_input.lower() == "approve":
        return {"approved": True, "feedback": ""}
    elif user_input.lower() == "reject":
        return {"approved": False, "feedback": "The Draft was Rejected."}
    elif user_input.lower() == "edit":
        feedback_text = input("Enter Your Feedback: ")
        return {"approved": False, "feedback": feedback_text}
    else:
        print("Invalid Input select from given options: (approve/reject/edit)")
        return {"approved": False, "feedback": ""}

def post_to_thread(state: AgentState):
    draft = state['draft']

    access_token = os.getenv("THREADS_ACCESS_TOKEN")

    #Step A Create Container
    step_a_url = f"https://graph.threads.net/v1.0/{os.getenv('THREADS_USER_ID')}/threads"
    step_a_params = {
        "media_type": "TEXT",
        "text": draft,
        "access_token": access_token
    }


    step_a_response = requests.post(step_a_url, params=step_a_params)
    creation_id = step_a_response.json()["id"]

    #Step B Publish 
    step_b_url = f"https://graph.threads.net/v1.0/{os.getenv('THREADS_USER_ID')}/threads_publish"
    step_b_params = {
        "creation_id": creation_id,
        "access_token": access_token
    }

    requests.post(step_b_url, params=step_b_params)

    return {"draft": draft}

#HElper function for conditional Edges
def should_post(state: AgentState):
    if state["approved"]:
        return "post"
    return "regenerate"

graph = StateGraph(AgentState)

graph.add_node("Research", research)
graph.add_node("Generate_Draft", generate_draft)
graph.add_node("Human_Review", human_review)
graph.add_node("Post_to_Thread", post_to_thread)

graph.add_edge("Research", "Generate_Draft")
graph.add_edge("Generate_Draft", "Human_Review")
graph.add_conditional_edges("Human_Review", should_post, {
    "post": "Post_to_Thread",
    "regenerate": "Generate_Draft"
})
graph.add_edge("Post_to_Thread", END)
graph.set_entry_point("Research")

app = graph.compile()

if __name__ == "__main__":
    topic = input("Enter a topic to post about: ")
    result = app.invoke({
        "topic": topic,
        "research": "",
        "draft": "",
        "approved": False,
        "feedback": ""
    })
    print("Successfully posted to Threads!")