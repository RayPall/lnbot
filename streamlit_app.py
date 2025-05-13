# streamlit_app.py
# ---------------------------------------------------------------------------
# Jednostránková aplikace:
#   • Generování LinkedIn příspěvku (odeslání na WEBHOOK_POST)
#   • Přidání nové persony (odeslání na WEBHOOK_PERSONA + okamžitá aktualizace listu)
# ---------------------------------------------------------------------------

import json
import requests
import streamlit as st

# --- Konstanta: Make webhooky -------------------------------------------------
WEBHOOK_POST    = "https://hook.eu2.make.com/6m46qtelfmarmwpq1jqgomm403eg5xkw"
WEBHOOK_PERSONA = "https://hook.eu2.make.com/9yo8y77db7i6do272joo7ybfoue1qcoc"   # ← doplň svoji URL

# --- Výchozí seznam person ----------------------------------------------------
DEFAULT_PERSONAS = [
    "Daniel Šturm", "Martin Cígler", "Marek Steiger",
    "Kristína Pastierik", "Lucie Jahnová"
]

# --- Inicializace session_state ----------------------------------------------
if "person_list" not in st.session_state:
    st.session_state.person_list = DEFAULT_PERSONAS.copy()

if "show_persona_form" not in st.session_state:
    st.session_state.show_persona_form = False

# ----------------------------------------------------------------------------- 
st.set_page_config(page_title="LinkedIn bot", page_icon="📝")
st.title("LinkedIn bot 📝")

# ===================== 1) GENERÁTOR PŘÍSPĚVKU =================================
with st.form("post_form"):
    topic = st.text_area("Jaké má být téma příspěvku?")
    persona = st.radio(
        "Čím stylem má být příspěvek napsán?",
        st.session_state.person_list
    )
    email = st.text_input("Na jaký e‑mail poslat draft?")
    submitted_post = st.form_submit_button("Odeslat")

# ---- Odeslat na Make ---------------------------------------------------------
if submitted_post:
    post_payload = {
        "personName":   persona,
        "postContent":  topic,
        "responseMail": email
    }

    with st.spinner("Generuji pomocí ChatGPT…"):
        try:
            res = requests.post(WEBHOOK_POST, json=post_payload, timeout=120)
            res.raise_for_status()
        except Exception as e:
            st.error(f"Chyba při komunikaci s Make: {e}")
            st.stop()

    # bezpečné vytažení klíče „post“
    try:
        post_text = res.json().get("post", "")
    except (ValueError, AttributeError):
        post_text = res.text

    post_md = post_text.strip().replace("\n", "  \n")   # 2 mezery = hard‑break
    st.success("Hotovo! Zde je vygenerovaný příspěvek:")
    st.markdown(post_md)

# ===================== 2) PŘIDAT NOVOU PERSONU ================================
st.markdown("---")
st.header("➕ Přidat novou personu")

# -- přepínač mezi tlačítkem a formulářem --------------------------------------
if not st.session_state.show_persona_form:
    if st.button("Přidat personu"):
        st.session_state.show_persona_form = True
        st.experimental_rerun()

else:
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

    # ---- Odeslat novou personu na Make ---------------------------------------
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
                rp = requests.post(WEBHOOK_PERSONA, json=persona_payload, timeout=30)
                rp.raise_for_status()
            except Exception as e:
                st.error(f"Chyba při ukládání: {e}")
                st.stop()

        # úspěch -> přidat do seznamu a obnovit UI
        st.session_state.person_list.append(name.strip())
        st.session_state.show_persona_form = False
        st.success("Persona uložena ✔️")
        st.experimental_rerun()
