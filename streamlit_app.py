# streamlit_app.py
# ---------------------------------------------------------------------------
#  ✍️  Vygenerovat příspěvek     (WEBHOOK_POST)
#  ➕  Přidat personu            (WEBHOOK_PERSONA)
#  🗑  Smazat personu            (WEBHOOK_DELETE_PERSONA)
# ---------------------------------------------------------------------------

import requests, streamlit as st

# --------- Make webhooky ------------------------------------------------------
WEBHOOK_POST           = "https://hook.eu2.make.com/6m46qtelfmarmwpq1jqgomm403eg5xkw"
WEBHOOK_PERSONA_ADD    = "https://hook.eu2.make.com/9yo8y77db7i6do272joo7ybfoue1qcoc"
WEBHOOK_PERSONA_DELETE = "https://hook.eu2.make.com/v95j3ouaspqnpbajtfeh9umh4qn537s7"

# --------- Výchozí seznam person ---------------------------------------------
DEFAULT_PERSONAS = [
    "Daniel Šturm", "Martin Cígler", "Marek Steiger",
    "Kristína Pastierik", "Lucie Jahnová"
]

# --------- Session‑state ------------------------------------------------------
if "person_list" not in st.session_state:
    st.session_state.person_list = DEFAULT_PERSONAS.copy()

def rerun():
    if hasattr(st, "rerun"):
        st.rerun()
    else:
        st.experimental_rerun()

# ------------------------------------------------------------------------------
st.set_page_config(page_title="LinkedIn bot", page_icon="📝")
st.title("LinkedIn bot")

tab_post, tab_persona = st.tabs(["✍️ Vygenerovat příspěvek", "🛠 Správa person"])

# ====================== 1)
