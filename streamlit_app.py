# streamlit_app.py
# ---------------------------------------------------------------------------
#  ▸ Záložka 1 –  ✍️  Vygenerovat příspěvek  (odesílá na WEBHOOK_POST)
#  ▸ Záložka 2 –  ➕  Přidat personu         (odesílá na WEBHOOK_PERSONA)
#  ▸ Po úspěšném přidání se jméno hned objeví v radiu na 1. záložce
# ---------------------------------------------------------------------------

import requests, streamlit as st

# --------- Make webhooky ------------------------------------------------------
WEBHOOK_POST    = "https://hook.eu2.make.com/6m46qtelfmarmwpq1jqgomm403eg5xkw"
WEBHOOK_PERSONA = "https://hook.eu2.make.com/9yo8y77db7i6do272joo7ybfoue1qcoc"

# --------- Výchozí seznam person ---------------------------------------------
DEFAULT_PERSONAS = [
    "Daniel Šturm", "Martin Cígler", "Marek Steiger",
    "Kristína Pastierik", "Lucie Jahnová"
]

# --------- Session‑state ------------------------------------------------------
if "person_list" not in st.session_state:
    st.session_state.person_list = DEFAULT_PERSONAS.copy()

def rerun():
    """verze‑safe rerun"""
    if hasattr(st, "rerun"):
        st.rerun()
    else:
        st.experimental_rerun()

# ------------------------------------------------------------------------------
st.set_page_config(page_title="LinkedIn bot", page_icon="📝")
st.title("LinkedIn bot")

tab_post, tab_persona = st.tabs(["✍️ Vygenerovat příspěvek", "➕ Přidat personu"])

# ====================== 1)  Vygenerovat příspěvek =============================
with tab_post:
    st.subheader("Vygenerovat LinkedIn příspěvek")
    with st.form("post_form"):
        topic = st.text_area("Jaké má být téma příspěvku?")
        persona = st.radio(
            "Čím stylem má být příspěvek napsán?",
            st.session_state.person_list
        )
        email = st.text_input("Na jaký e‑mail poslat draft?")
        submitted_post = st.form_submit_button("Odeslat")

    if submitted_post:
        payload = {
            "personName":   persona,
            "postContent":  topic,
            "responseMail": email
        }

        with st.spinner("Generuji pomocí ChatGPT…"):
            try:
                res = requests.post(WEBHOOK_POST, json=payload, timeout=120)
                res.raise_for_status()
            except Exception as e:
                st.error(f"Chyba při komunikaci s Make: {e}")
                st.stop()

        try:
            post_text = res.json().get("post", "")
        except Exception:
            post_text = res.text

        post_md = post_text.strip().replace("\n", "  \n")
        st.success("Hotovo! Zde je vygenerovaný příspěvek:")
        st.markdown(post_md)

# ====================== 2)  Přidat personu ====================================
with tab_persona:
    st.subheader("Přidat novou personu")

    with st.form("persona_form", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            name  = st.text_input("Jméno*")
            role  = st.text_input("Role / pozice*")
            tone  = st.text_area("Tone of Voice*")
        with col2:
            style   = st.text_area("Styl psaní*")
            lang    = st.selectbox("Jazyk*", ("Čeština", "Slovenština", "Angličtina", "Jiný"))
            sample  = st.text_area("Ukázkový příspěvek*")

        submitted_persona = st.form_submit_button("Uložit personu")

    if submitted_persona:
        if not name.strip():
            st.error("Jméno je povinné.")
            st.stop()

        persona_payload = {
            "name":     name.strip(),
            "role":     role.strip(),
            "tone":     tone.strip(),
            "style":    style.strip(),
            "language": lang,
            "sample":   sample.strip()
        }

        with st.spinner("Ukládám personu…"):
            try:
                res_p = requests.post(WEBHOOK_PERSONA, json=persona_payload, timeout=30)
                res_p.raise_for_status()
            except Exception as e:
                st.error(f"Chyba při ukládání: {e}")
                st.stop()

        # přidej jméno do runtime seznamu a přepni zpět na první tab
        st.session_state.person_list.append(name.strip())
        st.success("Persona uložena ✔️")
        rerun()                  # přenačte stránku → radio na 1. tab má novou personu
