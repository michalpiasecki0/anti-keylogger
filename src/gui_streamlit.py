import shlex
import subprocess
from os.path import exists
import psutil
import getopt
import sys
import os.path
import streamlit as st
import pandas as pd
import numpy as np
import dummy

st.set_page_config(
    layout='wide'
)

def process_single_entry(line: str):
    if line:
        data = line.split(sep=" ")
        data = list(filter(None, data))
        name = data[0]
        pid = data[1]
        port = data[-2].split(sep=':')[-1]
        return name, pid, port
    
def add_app():
    if action == 'Add to blacklist':
        st.session_state.black_list.append(app)
    elif action == "Add to accepted":
        st.session_state.white_list.append(app)

    
st.title('Projekt anti-keyloggera')
st.subheader("Aplikacja służąca do wyszukiwania potencjalnych złośliwych keyloggerów")
st.write(   
         ":blue[Potential keyloggers]: lista aplikacji podejrzanych o bycie złośliwymi keyloggerami  \n"
         ":green[Accepted list]: aplikacje, zaakceptowane przez użytkownika i traktowane jako bezpieczne  \n"
         ":red[Blacklist]: aplikacje ze złośliwym oprogramowaniem, są one automatycznie usuwane  ")
with st.sidebar:
    st.subheader("Authors")
    lst = ['Michal Piasecki', 'Bartosz Tomala', 'Jakub Gazewski']

    for i in lst:
        st.markdown("- " + i)


if 'black_list' not in st.session_state:
    st.session_state.black_list = []
if 'white_list' not in st.session_state:
    st.session_state.white_list = []


time = 1



start_button = st.button("Start scanning", 
                            key='start_button')
    
if 'start_button' in st.session_state:

    command = shlex.split('lsof -nP -iTCP:587 -iTCP:465 -iTCP:2525, -iTCP:22')
    proc = subprocess.Popen(command, stdout=subprocess.PIPE)
    out, err = proc.communicate()
    output = out.decode()
    time += 1
    possible_proc = output.split(sep="\n")[1:-1]
    procs_info = []
    if possible_proc:
        procs_info = [process_single_entry(line) for line in possible_proc]
    st.subheader("Potential keyloggers:")
    combined_black_white = st.session_state.black_list + st.session_state.white_list
    df = pd.DataFrame(
        [
            {'Application name': {proc[0]}, 'Process ID (PID)': {int(proc[1])}, "Port": {int(proc[2])}} for proc in procs_info
            if proc[0] not in combined_black_white
        ]
                      )
    c1, c2, c3 = st.columns((1 , 0.5, 0.5))
    with c1:
        st.table(df)
    st.subheader("Classify app")
    c1, c2, c3, _ = st.columns((1,1,1,2))
    with c1:
        app = st.selectbox(label='Apps', options = [proc[0] for proc in procs_info if proc[0] not in combined_black_white])
    with c2:
        action = st.selectbox(label="Action", options=['Add to blacklist', 'Add to accepted'])
    with c3:
        st.write("")
        st.write("")
        confirm_button = st.button(label='Confirm', key='confirm_button', on_click=add_app)

    c1, c2, _ = st.columns((1, 1, 1))
    with c1:
        st.write(":red[Blacklist]")
        st.write(st.session_state.black_list)
    with c2:
        st.write(":green[Accepted list]")
        st.write(st.session_state.white_list)
    for process in procs_info:
        name, pid, _ = process[0], process[1], process[2]
        p = psutil.Process(int(pid))
        if name in st.session_state.black_list:
            p.kill()
            with c1:
                st.warning(f'Blacklist application :red[{name}] found running. Process automatically terminated')
        elif name in st.session_state.white_list:
            with c2:
                st.write(f':green[{name}] is running')