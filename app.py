import os
from constants import user_data
import streamlit as st
from openai import OpenAI
from workflow import give_informed_resp
import logging.config

logging.config.fileConfig(
    'logging.config',
    disable_existing_loggers=False)
logger = logging.getLogger(__name__)
st.title("sell**A**r**I**")

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

cols = st.columns(4)

with cols[0]:
    if st.button("Franz"):
        st.session_state.input = "Franz"
        st.session_state.user_data = user_data['franz']
        st.session_state.messages = []
with cols[1]:
    if st.button("Sally"):
        st.session_state.input = "Sally"
        st.session_state.user_data = user_data['sally']
        st.session_state.messages = []
with cols[2]:
    if st.button("Peter"):
        st.session_state.input = "Peter"
        st.session_state.user_data = user_data['peter']
        st.session_state.messages = []
with cols[3]:
    if st.button("Viola"):
        st.session_state.input = "Viola"
        st.session_state.messages = []

if "input" in st.session_state:
    st.write("Using " + st.session_state.input + " as test input")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# check if everything is in order to make the introductory message
if "messages" in st.session_state and "user_data" in st.session_state and len(st.session_state.messages) == 0:
    with st.chat_message("assistant"):
        stream = give_informed_resp(user_data=st.session_state.user_data, context_memory=st.session_state.messages,first=True)
        response = st.write_stream(stream)
    st.session_state.messages.append({"role": "assistant", "content": response})

if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        stream = give_informed_resp(user_data=st.session_state.user_data, context_memory=st.session_state.messages)
        response = st.write_stream(stream)
    st.session_state.messages.append({"role": "assistant", "content": response})
