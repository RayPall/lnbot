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

# ====================== 2)  Správa person =====================================
with tab_persona:
    st.subheader("➕ Přidat novou personu")
    with st.form("persona_add_form", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            name   = st.text_input("Jméno*")
            role   = st.text_input("Role / pozice*")
            tone   = st.text_area("Tone of Voice*")
        with col2:
            style  = st.text_area("Styl psaní*")
            lang   = st.selectbox("Jazyk*", ("Čeština", "Slovenština", "Angličtina", "Jiný"))
            sample = st.text_area("Ukázkový příspěvek*")

        submitted_persona_add = st.form_submit_button("Uložit personu")

    if submitted_persona_add:
        if not name.strip():
            st.error("Jméno je povinné.")
            st.stop()

        payload_add = {
            "name":     name.strip(),
            "role":     role.strip(),
            "tone":     tone.strip(),
            "style":    style.strip(),
            "language": lang,
            "sample":   sample.strip()
        }

        with st.spinner("Ukládám personu…"):
            try:
                requests.post(WEBHOOK_PERSONA_ADD, json=payload_add, timeout=30).raise_for_status()
            except Exception as e:
                st.error(f"Chyba při ukládání: {e}")
                st.stop()

        st.session_state.person_list.append(name.strip())
        st.success("Persona uložena ✔️")
        rerun()

    # --------------- Mazání persony ------------------------------------------
    st.markdown("---")
    st.subheader("🗑 Smazat existující personu")

    if st.session_state.person_list:
        with st.form("persona_delete_form"):
            to_delete = st.selectbox("Vyber personu k odstranění",
                                     st.session_state.person_list)
            submitted_delete = st.form_submit_button("Smazat personu",
                                                     help="Trvale odstraní z tabulky")

        if submitted_delete:
            payload_del = {"name": to_delete}
            with st.spinner("Odebírám personu…"):
                try:
                    requests.post(WEBHOOK_PERSONA_DELETE, json=payload_del, timeout=30).raise_for_status()
                except Exception as e:
                    st.error(f"Chyba při mazání: {e}")
                    st.stop()

            # odstraň lokálně a aktualizuj UI
            st.session_state.person_list = [p for p in st.session_state.person_list if p != to_delete]
            st.success(f"Persona „{to_delete}“ byla smazána ✔️")
            rerun()
    else:
        st.info("Žádné persony k dispozici.")
