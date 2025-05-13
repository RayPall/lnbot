import os, json, requests, streamlit as st

# --- dvě webhook URL -----------------------------------------------------------
POST_WEBHOOK        = "https://hook.eu2.make.com/6m46qtelfmarmwpq1jqgomm403eg5xkw"
ADD_PERSONA_WEBHOOK = os.getenv(
    "ADD_PERSONA_WEBHOOK",
    "https://hook.eu2.make.com/xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")  # ⬅︎ nový webhook

st.set_page_config(page_title="LinkedIn bot", page_icon="📝")

# ------------------------------------------------------------------------------
tab_post, tab_persona = st.tabs(["✍️ Vygenerovat příspěvek", "➕ Přidat personu"])

# ═════════════════════ 1) GENEROVÁNÍ PŘÍSPĚVKU ════════════════════════════════
with tab_post:
    st.header("Vygenerovat příspěvek")
    with st.form("post_form"):
        topic = st.text_area("Jaké má být téma příspěvku?")
        persona = st.radio(
            "Čím stylem má být příspěvek napsán?",
            ("Daniel Šturm", "Martin Cígler", "Marek Steiger",
             "Kristína Pastierik", "Lucie Jahnová"))
        email = st.text_input("Na jaký e‑mail poslat draft?")
        send_post = st.form_submit_button("Odeslat")

    if send_post:
        payload = {
            "personName": persona,
            "postContent": topic,
            "responseMail": email
        }
        with st.spinner("Generuji pomocí ChatGPT…"):
            res = requests.post(POST_WEBHOOK, json=payload, timeout=120)

        if not res.ok:
            st.error(f"Chyba {res.status_code}: {res.text}")
            st.stop()

        try:
            post = res.json()["post"]
        except Exception:
            # fallback – odříznout { "post": "..."}
            raw = res.text.strip()
            post = raw.split(":", 1)[1].rsplit("}", 1)[0].strip(' "')

        st.success("Hotovo! Zde je vygenerovaný příspěvek:")
        st.markdown(post.replace("\n", "  \n"))

# ═════════════════════ 2) PŘIDÁNÍ PERSONY ════════════════════════════════════
with tab_persona:
    st.header("Přidat novou personu")
    with st.form("persona_form", clear_on_submit=True):
        p_name   = st.text_input("Jméno*", max_chars=50)
        p_role   = st.text_input("Role / pozice*", max_chars=80)
        p_tone   = st.text_area("Tone of Voice*", height=70)
        p_style  = st.text_area("Styl psaní*", height=70)
        p_lang   = st.selectbox("Jazyk*", ["Čeština", "Angličtina", "Slovenština"])
        p_sample = st.text_area("Ukázkový příspěvek*", height=120)

        add_persona = st.form_submit_button("Uložit personu")

    if add_persona:
        if not all([p_name, p_role, p_tone, p_style, p_sample]):
            st.error("Vyplň prosím všechna povinná pole označená *")
            st.stop()

        persona_payload = {
            "name":     p_name,
            "role":     p_role,
            "tone":     p_tone,
            "style":    p_style,
            "language": p_lang,
            "sample":   p_sample
        }

        with st.spinner("Ukládám personu do Google Sheetu…"):
            resp = requests.post(ADD_PERSONA_WEBHOOK,
                                 json=persona_payload,
                                 timeout=30)

        if resp.ok:
            st.success("Persona byla uložena ✅")
        else:
            st.error(f"Nepodařilo se uložit personu: {resp.status_code} {resp.text}")
