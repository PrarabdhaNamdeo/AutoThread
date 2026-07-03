import streamlit as st
from agent import research, generate_draft, app, post_to_thread

st.title("Auto Thread")

if "draft" not in st.session_state:
    st.session_state["draft"] = ""

if "stage" not in st.session_state:
    st.session_state["stage"] = "input"

if "feedback" not in st.session_state:
    st.session_state["feedback"] = ""

if "topic" not in st.session_state:
    st.session_state["topic"] = ""

if "research" not in st.session_state:
    st.session_state["research"] = ""

if st.session_state["stage"] == "review":
    st.write(st.session_state["draft"])
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Approve"):
            state = {
                "draft": st.session_state["draft"],
                "approved": True,
                "feedback": ""
            }
            post_to_thread(state)
            st.session_state["stage"] = "success"
            
    with col2:
        if st.button("Reject"):
            st.session_state["stage"] = "input"
            
    with col3:
        if st.button("Edit"):   
                st.session_state["stage"] = "edit"

if st.session_state["stage"] == "input":
    topic = st.text_input("Enter Topic", key="topic_input")
    if st.button("Generate Thread"):
        topic = st.session_state["topic_input"]
        if not topic:
            st.error("Please enter a topic before generating!")
        else:
            st.session_state["topic"] = topic
            with st.spinner("Researching and generating draft..."):
                try:
                    state = {
                        "topic": topic,
                        "research": "",
                        "draft": "",
                        "approved": False,
                        "feedback": ""
                    }
                    research_result = research(state)
                    state.update(research_result)
                    st.session_state["research"] = research_result["research"]
                    draft_result = generate_draft(state)
                    st.session_state["draft"] = draft_result["draft"]
                    st.session_state["stage"] = "review"
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
                    import traceback
                    st.code(traceback.format_exc())

if st.session_state["stage"] == "edit":
    topic = st.session_state["topic"]
    #st.write(st.session_state["draft"])  --> to show
    feedback = st.text_input("Enter Your Feedback")
    if st.button("Regenerate"):
        state = {
            "topic": topic,
            "research": st.session_state["research"],
            "draft": "",
            "approved": False,
            "feedback": feedback
        }
        draft_result = generate_draft(state)
        st.session_state["draft"] = draft_result["draft"]
        st.session_state["stage"] = "review"

if st.session_state["stage"] == "success":
    st.write("Your Thread has been Posted Successfully!")
    if st.button("Post Another"):
        st.session_state["stage"] = "input"
        st.session_state["draft"] = ""
        st.session_state["feedback"] = ""
        st.session_state["research"] = ""