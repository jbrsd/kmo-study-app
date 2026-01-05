import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(page_title="KMO Study Pro", layout="centered")

# --- STICKY HEADER & CARDS CSS ---
st.markdown("""
    <style>
    /* This makes the button area stay at the top of the screen when scrolling */
    .stApp > header {
        background-color: transparent;
    }
    
    .sticky-box {
        position: sticky;
        top: 2rem;
        z-index: 1000;
        background-color: #0e1117;
        padding-bottom: 20px;
        border-bottom: 2px solid #31333f;
    }

    .question-card {
        background-color: #262730;
        color: #ffffff;
        padding: 25px;
        border-radius: 12px;
        border-left: 8px solid #ff4b4b;
        font-size: 20px;
        line-height: 1.4;
        white-space: pre-wrap;
        font-family: 'Source Sans Pro', sans-serif;
        margin-top: 20px;
    }
    
    .subject-label {
        color: #ff4b4b;
        font-weight: bold;
        text-transform: uppercase;
        font-size: 14px;
        letter-spacing: 2px;
        margin-top: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

def get_query(sql, params=()):
    conn = sqlite3.connect('kmo_database.db')
    df = pd.read_sql_query(sql, conn, params=params)
    conn.close()
    return df

# --- SIDEBAR (Filters only) ---
st.sidebar.title("🎯 Filters")
topics = get_query("SELECT DISTINCT topic FROM questions ORDER BY topic")['topic'].tolist()
choice = st.sidebar.selectbox("Subject", ["All"] + topics)
search = st.sidebar.text_input("Search")

# --- MAIN INTERACTION AREA (Buttons at the TOP) ---
# We use a container to keep our buttons in a static location
with st.container():
    st.title("🏆 KMO Student Portal")
    
    col1, col2 = st.columns(2)
    
    with col1:
        new_q = st.button("New Question 🎲", use_container_width=True)
    
    with col2:
        # If not answered, show 'Check Answer'. If answered, show 'Next Question'
        # This button is now in the EXACT same spot for both states.
        if st.session_state.get('ans', False):
            action_btn = st.button("Next Question ➡️", use_container_width=True)
        else:
            action_btn = st.button("Check Answer ✅", use_container_width=True)

# --- LOGIC ---
if new_q or 'q' not in st.session_state or action_btn and st.session_state.get('ans', False):
    sql = "SELECT * FROM questions WHERE 1=1"
    p = []
    if choice != "All": sql += " AND topic = ?"; p.append(choice)
    if search: sql += " AND question LIKE ?"; p.append(f"%{search}%")
    sql += " ORDER BY RANDOM() LIMIT 1"
    res = get_query(sql, p)
    if not res.empty:
        st.session_state.q = res.iloc[0]
        st.session_state.ans = False
        if action_btn: st.rerun()

elif action_btn and not st.session_state.get('ans', False):
    st.session_state.ans = True
    st.rerun()

# --- DISPLAY AREA (Question appears BELOW buttons) ---
if 'q' in st.session_state and st.session_state.q is not None:
    q = st.session_state.q
    
    # The Subject and Question now expand DOWNWARD, leaving the buttons above unmoved
    st.markdown(f'<div class="subject-label">{q["topic"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="question-card">{q["question"]}</div>', unsafe_allow_html=True)
    
    if st.session_state.ans:
        st.write("")
        st.success(f"### Answer: {q['answer']}")