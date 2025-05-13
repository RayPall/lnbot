# streamlit_app.py
# ---------------------------------------------------------------------------
# Aplikace pro:
#   • generování LinkedIn příspěvků (WEBHOOK_POST)
#   • přidávání nových person (WEBHOOK_PERSONA) – po uložení se hned objeví v seznamu
# ---------------------------------------------------------------------------

import requests, streamlit as st

# --- Make webhooky ------------------------------------------------------------
WEBHOOK_POST    = "https://hook.eu2.make.com/6m46qtelfmarmwpq1jqgomm403eg5xkw"
WEBHOOK_PERSONA = "https://hook.eu2.make.com/9yo8y77db7i6do272joo7ybfoue1qcoc"   # ← doplň

# --- Výchozí seznam person ----------------------------------------------------
DEFAULT_PERSONAS = [
    "Daniel Šturm", "Martin Cígler", "Marek Steiger",
    "Kristína Pastierik", "Lucie Jahnová"
]

# --- Session‑state ------------------------------------------------------------
if "person_list" not in st.session_state:
    st.session_state.person_list = DEFAULT_PERSONAS.copy()

if "show_persona_form" not in st.session_state:
    st.session_state.show_persona_form = False

# --- pomocná funkce pro rerun (kompatibilita různých verzí Streamlit) ---------
def do_rerun():
    if hasattr(st, "rerun"):               # Streamlit ≥ 1.26
        st.rerun()
    else:                                  # starší verze
        st.experimental_rerun()

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

    # bezpečné vytažení textu
    try:
        post_text = res.json().get("post", "")
    except Exception:
        post_text = res.text

    post_md = post_text.strip().replace("\n", "  \n")   # 2 mezery = hard‑break
    st.success("Hotovo! Zde je vygenerovaný příspěvek:")
    st.markdown(post_md)

# ===================== 2) PŘIDÁNÍ NOVÉ PERSONY ================================
st.markdown("---")
st.header("➕ Přidat novou personu")

if not st.session_state.show_persona_form:
    st.button("Přidat personu", key="show_form_btn",
              on_click=lambda: st.session_state.update(show_persona_form=True))
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

        # přidej jméno do runtime seznamu a zavři formulář
        st.session_state.person_list.append(name.strip())
        st.session_state.show_persona_form = False
        st.success("Persona uložena ✔️")
        do_rerun()
