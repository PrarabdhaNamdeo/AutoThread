# Auto Thread 🤖

An agentic AI that researches any topic, writes a Threads post, and publishes it — but only after **you** approve it.

---

## What It Does

Auto Thread is an AI-powered content agent that automates the process of writing and posting to Threads (Instagram's text platform). You give it a topic, it searches the web for real-time information, drafts an engaging post using an LLM, shows it to you for review, and only publishes it once you say so.

The key idea: the AI does the research and writing grunt work, but the final decision is always yours.

---

## Demo Flow

```
User enters topic → Agent researches web → LLM drafts post → Human reviews →
    ├── Approve → Posts to Threads ✅
    ├── Edit → Give feedback → Regenerates → Review again 🔄
    └── Reject → Start over ❌
```

---

## Architecture

```
research node → generate_draft node → [HITL: human_review via Streamlit UI] → post_to_thread node
                        ↑                                                              |
                        |_____________ if rejected/edited _____________________________|
```

Built with **LangGraph** as the orchestration layer — each step (research, generate, post) is a node in a stateful graph. LangGraph handles the conditional routing between nodes, making the looping HITL logic clean and explicit rather than a mess of if/else statements in a single script.

---

## Tech Stack

| Tool | Purpose |
|---|---|
| LangGraph | Agentic workflow orchestration and HITL state management |
| Groq (llama-3.3-70b) | LLM for generating Threads post drafts |
| Tavily API | Real-time web research on the given topic |
| Threads API (Meta) | Publishing approved posts to Threads |
| Streamlit | Frontend UI for topic input and human review |
| Python-dotenv | Secure credential management |

---

## Why LangGraph?

LangGraph makes the agentic flow — especially the looping HITL logic — clean and maintainable. Instead of writing complex control flow manually, each step is a clearly defined node with explicit edges between them. The conditional edge after human review (approve → post, reject → regenerate) is a first-class feature of LangGraph, not a hack.

## Why HITL?

Without Human-in-the-Loop, the agent would post directly to your public Threads profile with zero oversight. A model can hallucinate facts, use the wrong tone, or generate something off-brand. HITL ensures you stay in control — the agent handles research and drafting, but the publish decision is always yours.

---

## Project Structure

```
auto-threads-agent/
├── agent.py          # LangGraph nodes, graph definition, Threads API integration
├── app.py            # Streamlit frontend with HITL review UI
├── get_token.py      # Utility to refresh long-lived Threads access token
├── .env              # API credentials (never commit this)
├── .gitignore
└── README.md
```

---

## Getting Your Threads Credentials

1. Go to [developers.facebook.com](https://developers.facebook.com)
2. Create a new app and select **"Access the Threads API"** as the use case
3. Add yourself as a Threads Tester under App Roles
4. Accept the tester invite from your Threads app on your phone
5. Generate an access token from the Testing section
6. Run `get_token.py` to exchange it for a long-lived token (valid 60 days)

---

## Token Refresh

Your Threads access token expires every 60 days. Run this to refresh it:

```bash
python get_token.py
```

Copy the new `access_token` from the output and update your `.env` file.

---

## Key Design Decisions

**Stateful graph over a simple script:** Using LangGraph's `StateGraph` means every node receives and returns a shared state dictionary (`AgentState`). This makes the data flow between research → generate → post explicit and debuggable.

**Tavily for research:** Rather than letting the LLM generate from training data alone (which may be outdated or hallucinated), Tavily fetches real-time web results that are injected into the prompt as context. This grounds the generated post in actual current information.

**Streamlit for HITL:** The terminal `input()` approach works but isn't demonstrable. Streamlit's session state perfectly mirrors LangGraph's state concept — both maintain data across interactions — making them a natural pair for this use case.

---

## What I'd Add Next

- OAuth flow so multiple users can connect their own Threads accounts
- Scheduled posting (post at a specific time after approval)
- Post history and analytics dashboard
- Multi-platform support (LinkedIn, Twitter/X)

---

## Author

**Prarabdha Namdeo**
- GitHub: [@PrarabdhaNamdeo](https://github.com/PrarabdhaNamdeo)
- Threads: [@_prarabdha_namdeo_](https://www.threads.net/@_prarabdha_namdeo_)
