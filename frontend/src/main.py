import streamlit as st
import requests
import json
import time

SERVR_IP = "<IP address of the server where the chatter is running>"

# some helper functions to print the messages
def write_chunks(r):
    data = r.json()
    if "chunks" not in data.keys():
        st.write("...")
    else:
        with st.container():
            col1, col2 = st.columns([1, 3])
            col1.write("Similarity (0 to 1)")
            col2.write("Wiki page with content")
            for c in data["chunks"]:
                sim, name, url = c.split(" || ")
                col1.write(round(float(sim), 2))
                col2.page_link(url, label=name, icon="🌎")

def write_answer(r):
    data = r.json()
    if "answer" not in data.keys():
        st.write("...")
    else:
        st.write(data["answer"])

# acutally defining the page's content ---------------------------------------------------------------
st.set_page_config(page_title="iwBot", page_icon="🚀")
st.title("iwBot 🚀📚")

st.write("Welcome to the iwb wiki bot! 🖖" + 
"We are currently in a beta version, so the system is meant for testing only. " +
"Please note, that giving feedback will save the question in order to further improve the system.")

st.subheader("What's your question?")
st.text_input(" ", key="question")

st.subheader("Retrieved document chunks")
r_chunks = requests.get(f"http://{SERVER_IP}:8000/chunks/{st.session_state.question}")
write_chunks(r_chunks)

st.subheader("Answer by llm, based on chunks")
r_answer = requests.get(f"http://{SERVER_IP}:8000/answer/{st.session_state.question}")
write_answer(r_answer)

# asking for and dealing with feedback --------------------------------------------------------------
def read_and_reset_feedback_states():
    for sk in ["bad", "ok", "good"]:
        if "{sk}_feedback" in st.session_state:
            del st.session_state["{sk}_feedback"]
            return sk
    return None

def save_feedback(bog):
    if bog is not None:
        with open(f"/app/feedback/{time.strftime('%Y-%m-%d_%H-%M-%S')}_{bog}", "w") as file:
            file.write(json.dumps({
                "question": st.session_state.question,
                "chunks": r_chunks.json(),
                "answer": r_answer.json()
            }, indent=4))
        
def save_bad_feedback():
    save_feedback("bad")
    
def save_ok_feedback():
    save_feedback("ok")

def save_good_feedback():
    save_feedback("good")

st.subheader("Help us improve and rate this answer...")
col1, col2, col3 = st.columns(3)
col1.button(label="💩 total nonsense", key="bad feedback", on_click=save_bad_feedback)
col2.button(label="🤔 partly usefull", key="ok feedback", on_click=save_ok_feedback)
col3.button(label="👍 actually helpfull", key="good feedback", on_click=save_good_feedback)

for sk in ["bad", "ok", "good"]:
    if st.session_state[f"{sk} feedback"]:
        st.write("Thanks for your feedback!")
        del st.session_state[f"{sk} feedback"]